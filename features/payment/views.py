from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from features.cart.models import Cart, CartItem
from features.order.models import Order, OrderItem


@login_required
def checkout(request):
    """
    View function to create a new order and save it to the database after checkout.
    """
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
    messages.success(request, f"Order placed successfully")

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

    return redirect("/order/my_order/")