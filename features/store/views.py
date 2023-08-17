from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from features.cart.models import Cart, CartItem
from features.clothes.models import Product
from features.clothes.decorators import seller_required


# Views common for all user types
def handler404(request):
    """
    Custom 404 error handler.
    """
    context = {'show_navbar_footer': False}
    return render(request, '404.html', context=context, status=404)


# Views for Customers
def home(request):
    """
    Render home page with a list of all products available in the database.
    """
    # Get all products from database
    product_list = Product.objects.all()

    context = {'show_navbar_footer': True, "product_list": product_list}
    return render(request, "home.html", context=context)


@login_required
def add_to_cart(request, product_id):
    """
    Adds the specified product to the user's cart and redirects to the home page.

    Args: product_id: The ID of the product to add to the cart.
    """
    # Get the product by ID or raise Http404 error if not found
    product = get_object_or_404(Product, id=product_id)

    # Retrieve or create the cart associated with the current user.
    cart, created = Cart.objects.get_or_create(customer=request.user)

    # Retrieve or create the cart item associated with the specified product and cart.
    # Increment the quantity of the item if it already exists.
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not item_created:
        cart_item.quantity += 1

    # Calculate the final price of the cart item, the total price of the cart and save it to the database.
    cart_item.final_item_price = cart_item.quantity * product.price
    cart_item.save()
    cart.update_total_price()
    messages.success(request, f"{product.name} added to cart")

    return redirect('/')


@login_required
def buy_now(request, product_id):
    """
    Add a product to cart and redirect to cart page for immediate checkout.

    Args: product_id: The ID of the product to add to the cart.
    """
    # Get the product by ID or raise Http404 error if not found
    product = get_object_or_404(Product, id=product_id)

    # Retrieve or create the cart associated with the current user.
    cart, created = Cart.objects.get_or_create(customer=request.user)

    # Retrieve or create the cart item associated with the specified product and cart.
    # Increment the quantity of the item if it already exists.
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not item_created:
        cart_item.quantity += 1
    
    # Calculate the final price of the cart item, the total price of the cart and save it to the database.
    cart_item.final_item_price = cart_item.quantity * product.price
    cart_item.save()
    cart.update_total_price()
    messages.success(request, f"{product.name} added to cart")

    return redirect('/cart/my_cart/')


# Views for Merchants
@login_required
@seller_required
def dashboard(request):
    """
    Renders the dashboard for the merchant.
    """
    context = {'show_navbar_footer': True}
    return render(request, "dashboard.html", context=context)