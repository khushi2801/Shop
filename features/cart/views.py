from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, redirect, render
from .models import (Cart, CartItem, Coupon, Product, UsedCoupon)
from .forms import CouponApplyForm


@login_required
def my_cart(request):
    """
    View function that displays the customer's cart with the ability to apply coupons to it.
    """
    # Retrieve or create the cart associated with the current customer.
    cart, created = Cart.objects.get_or_create(customer=request.user)

    # Retrieve all coupons and exclude those that have already been used by the customer
    coupons = Coupon.objects.all()
    unused_coupons = Coupon.objects.exclude(id__in=UsedCoupon.objects.filter(customer=request.user, active=False).values('coupon_id'))

    # Create a form to apply coupons to the cart
    form = CouponApplyForm(request.POST or None)
    
    if form.is_valid():
        # If form is valid extract the coupon code entered by the customer, retrieve a coupon with 
        # the entered code and check its validilty
        coupon_code = form.cleaned_data['code']
        try:
            coupon = Coupon.objects.get(code=coupon_code)
            customer_coupon, created = UsedCoupon.objects.get_or_create(customer=request.user, coupon=coupon)
            if customer_coupon.active:
                cart.customer_coupon = customer_coupon
                cart.apply_coupon()
                messages.success(request, f"Coupon '{coupon_code}' applied successfully.")
            else:
                messages.error(request, f"Invalid coupon code '{coupon_code}'")
        except ObjectDoesNotExist:
            messages.error(request, f"Invalid coupon code '{coupon_code}'")
        return redirect('cart:my_cart')
    
    context = {'show_navbar_footer': True, 'cart': cart, 'unused_coupons': unused_coupons, 'coupon_form':form}
    return render(request, 'cart/cart.html', context)


@login_required
def update_cart_items(request, product_id, quantity):
    """
    View function that updates the quantity of a product in the customer's cart or removes it from the cart entirely.

    Args: product_id: The ID of the product being updated.
          quantity: The new quantity of the product being updated, or None if the product is being removed from the cart.
    """
    # Retrieve the cart for the current customer
    cart = get_object_or_404(Cart, customer=request.user)

    # Get the product by ID or raise Http404 error if not found
    product = get_object_or_404(Product, id=product_id)

    # Retrieve the cart item for the product, if it exists
    cart_item = CartItem.objects.filter(cart__customer=request.user, product=product).first()

    # If a cart item exists and a new quantity was specified, update the quantity and final item price
    # If quantity = 0, remove the cart item entirely
    if cart_item and quantity:
        cart_item.quantity = quantity
        cart_item.final_item_price = product.price * quantity
        cart_item.save()
    elif not quantity:
        cart_item.delete()

    # Update the total price of the cart
    cart.update_total_price()

    # If a coupon is applied to the cart, re-apply it after the cart item update
    if cart.customer_coupon:
        cart.apply_coupon()
        cart.save()

    return redirect('/cart/my_cart/')


@login_required
def apply_coupon(request, coupon_code):
    """
    Applies the given coupon to the customer's cart and redirects to the cart page.
    
    Args: coupon_code: str representing the code of the coupon to apply
    """
    # Retrieve the customer's cart
    cart = get_object_or_404(Cart, customer=request.user)

    # Retrieve the coupon with the given code and apply to the customer's cart
    coupon = get_object_or_404(Coupon, code=coupon_code)
    customer_coupon, created = UsedCoupon.objects.get_or_create(customer=request.user, coupon=coupon)
    cart.customer_coupon = customer_coupon
    cart.apply_coupon()
    messages.success(request, f"Coupon '{coupon}' applied successfully.")

    return redirect('/cart/my_cart/')