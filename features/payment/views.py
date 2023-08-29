import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from features.cart.models import Cart, CartItem
from features.order.models import Order, OrderItem


@login_required
def checkout_cart(request):
    """
    View function to create a new order and save it to the database after checkout.
    """
    stripe.api_key = settings.STRIPE_SECRET_KEY

    # Get the cart items for the current customer
    cart_items = CartItem.objects.filter(cart__customer=request.user)

    line_items = []
    for cart_item in cart_items:
        line_items.append({
            "price_data": {
                "currency": "inr",
                "unit_amount": int(cart_item.final_item_price / cart_item.quantity),
                "product_data": {
                    "name": cart_item.product.name,
                },
            },
            "quantity": cart_item.quantity,
        })

    checkout_session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=line_items,
        mode="payment",
        billing_address_collection="required",
        phone_number_collection={"enabled": True},
        success_url=request.build_absolute_uri(reverse('payment:checkout_success')),
        cancel_url=request.build_absolute_uri(reverse('payment:checkout_fail')),
    )

    request.session['valid_payment_session_id'] = checkout_session.id

    return redirect(checkout_session.url)


@login_required
def checkout_success(request):
    valid_payment_session_id = request.session.get('valid_payment_session_id')

    if valid_payment_session_id:
        # Get the cart and the cart items for the current customer
        cart = get_object_or_404(Cart, customer=request.user)
        cart_items = CartItem.objects.filter(cart__customer=request.user)
        order_items = []

        # Create a billing address for the order using the user's profile
        billing_address = f"{request.user.profile.address}, {request.user.profile.city}, {request.user.profile.state}, {request.user.profile.country}, {request.user.profile.pin}"

        # Create a new order instance and save it to the database
        order = Order(cart=cart, customer=request.user, billing_address=billing_address, contact=request.user.profile.contact, 
                      total_price=cart.total_price, discount=cart.discount, final_price=cart.final_price)
        if cart.customer_coupon is not None:
            order.coupon = cart.customer_coupon.coupon
        order.save()

        # Create a list of order items and add them to the new order
        for item in cart_items:
            order_item = OrderItem(order=order, product=item.product,
                                   quantity=item.quantity, final_item_price=item.final_item_price)
            order_items.append(order_item)
        OrderItem.objects.bulk_create(order_items)
                
        # Deactivate the used coupon, if any
        if cart.customer_coupon:
            cart.customer_coupon.active = False
            cart.customer_coupon.save()

        # Delete cart items and update the cart's total price
        cart_items.delete()
        cart.update_total_price()

        context = {
            'show_navbar_footer': True,
        }
        return render(request, 'payment/success.html', context)
        
    raise Http404("Incorrect session ID")
    

@login_required
def checkout_fail(request):
    context = {
        'show_navbar_footer': True,
    }
    return render(request, 'payment/fail.html', context)