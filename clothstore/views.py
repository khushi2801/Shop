import datetime
import re
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.forms import model_to_dict
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from weasyprint import HTML
from clothstore.models import (Cart, CartItem, Coupon, Order, OrderItem, Product, UsedCoupon)
from .decorators import product_admin_required
from .forms import (CouponApplyForm, ProductForm, ProfileUpdateForm, UserAuthenticationForm, UserForm, UserUpdateForm)


# Views common for all user types
def handler404(request):
    """
    Custom 404 error handler.
    """
    context = {'show_navbar_footer': False}
    return render(request, '404.html', context=context, status=404)


def signup_view(request):
    """
    Renders a signup form for both regular users and product administrators. 
    Handles form submissions, checks form validity, creates a new user account, 
    authenticates the user, logs in the user, and redirects them to the appropriate 
    page based on their user type. Displays error messages if the form is invalid.
    """
    error_list = []

    if request.method == "POST":
        form = UserForm(request.POST)

        # Store errors to displays if form is invalid
        error_list = re.sub(r'\*\s*(password2|email)\n', '', form.errors.as_text())
        error_list = list(re.sub(r'\*.*?', '', error_list).split("\n"))

        if form.is_valid():
            form.save()
            messages.success(request, f"Account created successfully")
            user = authenticate(email=form.cleaned_data['email'], password=form.cleaned_data['password1'])
            login(request, user)
            messages.success(request, f"Welcome {user.name}")
            if form.cleaned_data['user_type'] == "ProductAdmin":
                return redirect("/clothstore/dashboard")
            else:
                return redirect("/")
        else:
            messages.error(request, "Invalid information!")
    
    # Render signup form if request method is not POST
    form = UserForm()
    context = {'show_navbar_footer': False, "signup_form": form, "error_list": error_list}
    return render(request, "signup.html", context=context)


def login_view(request):
    """
    Renders a login form and handles form submissions. Checks the validity of 
    the submitted form and authenticates the user. If authentication is successful,
    logs in the user, displays a welcome message, and redirects the user to 
    the appropriate page based on their user type. Displays error messages if the 
    form is invalid or if authentication fails.
    """
    if request.method == "POST":
        form = UserAuthenticationForm(request.POST)

        if form.is_valid():
            user = authenticate(email=form.cleaned_data['email'], password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                messages.info(request, f"Welcome {user.name}")
                if user.user_type == "ProductAdmin":
                    return redirect("/clothstore/dashboard/")
                else:
                    return redirect("/")
            else:
                messages.error(request, "Invalid email or password")
        else:
            messages.error(request, "Invalid email or password")

    # Render login form if request method is not POST
    form = UserAuthenticationForm()
    context = {'show_navbar_footer': False, "login_form": form}
    return render(request, "login.html", context=context)


@login_required
def logout_view(request):
    """
    Logs out the authenticated user and redirects them to the homepage.
    """
    logout(request)
    messages.success(request, "You have successfully logged out")
    return redirect("/")


@login_required
def profile_view(request):
    """
    Renders the user's profile page with their profile data.
    """
    # Convert user's profile object to dictionary
    user_data = model_to_dict(request.user.profile)

    context = {'show_navbar_footer': True, "user_data": user_data}
    return render(request, "profile.html", context=context)


@login_required
def update_profile_view(request):
    """
    Renders the profile update page and handles the submission of the profile update form.
    """
    
    if request.method == "POST":
        # Create user update and profile update forms with POST data and files
        u_form = UserUpdateForm(request.POST or None, request.FILES or None, instance=request.user)
        p_form = ProfileUpdateForm(request.POST or None, request.FILES or None, instance=request.user.profile)
        
        # If both forms are valid, save the updated user and profile data and redirect to the profile page
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f"Profile details updated successfully")
            return redirect("/clothstore/profile/")
    else:
        # Create user update and profile update forms with current user data
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    
    context =  {'show_navbar_footer': True, "user_update_form": u_form, "profile_update_form": p_form}
    return render(request, "update_profile.html", context=context)


# Views for Customers
def home_view(request):
    """
    Render home page with a list of all products available in the database.
    """
    # Get all products from database
    product_list = Product.objects.all()

    context = {'show_navbar_footer': True, "product_list": product_list}
    return render(request, "home.html", context=context)


@login_required
def product_detail_view(request, product_id):
    """
    Renders the product detail page for a given product.

    Args: product_id: ID of the product to display
    """
    # Get the product with the given ID and convert the product object to a dictionary to pass to the template
    p = Product.objects.get(id=product_id)
    product = model_to_dict(p)

    context = {'show_navbar_footer': True, "product": product}
    return render(request, "product_detail.html", context=context)


@login_required
def add_to_cart(request, product_id):
    """
    Adds the specified product to the user's cart and redirects to the home page.

    Args: product_id: The ID of the product to add to the cart.
    """
    # Get the product by ID or raise Http404 error if not found
    product = get_object_or_404(Product, id=product_id)

    # Retrieve or create the cart associated with the current user.
    cart, created = Cart.objects.get_or_create(user=request.user)

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

    return redirect('/clothstore/home/')


@login_required
def buy_now(request, product_id):
    """
    Add a product to cart and redirect to cart page for immediate checkout.

    Args: product_id: The ID of the product to add to the cart.
    """
    # Get the product by ID or raise Http404 error if not found
    product = get_object_or_404(Product, id=product_id)

    # Retrieve or create the cart associated with the current user.
    cart, created = Cart.objects.get_or_create(user=request.user)

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

    return redirect('/clothstore/cart/')


@login_required
def my_order_view(request):
    """
    View to display the orders made by the user.
    """
    # Get all active orders made by the user
    active_orders = Order.objects.filter(user=request.user, status=True)

    # Get all cancelled orders made by the user
    cancelled_orders = Order.objects.filter(user=request.user, status=False)

    context = {'show_navbar_footer': True, "active_orders": active_orders, "cancelled_orders": cancelled_orders}
    return render(request, "my_order.html", context=context)


@login_required
def order_operations(request, order_id):
    """
    Handles various operations related to orders like displaying order summary and cancelling orders.

    Args: order_id: The ID of the order to perform the operation on.
    """
    # Get the order for the given id and check if it belongs to the current user
    order = Order.objects.get(user=request.user, id=order_id)

    # If the URL contains 'order_summary', render the order summary page and if the URL contains 
    # 'cancel_order' and the order is not already cancelled, cancel the order
    if 'order_summary' in request.path_info:
        context = {'show_navbar_footer': True, "order": order, "show_print_button": True}
        return render(request, "order_summary.html", context=context)
    elif 'cancel_order' in request.path_info:
        if order.status:
            order.status = False
            order.save()
            messages.success(request, f"Order Cancelled")
    
    return redirect('/clothstore/my_order/')


@login_required
def generate_pdf(request, order_id):
    """
    This function generates a PDF of the order summary for the given order ID.
    
    Args: order_id: ID of the order to generate the PDF for.
    """
    # Get the order object for the given order ID and generate HTML string for the order object
    order = Order.objects.get(user=request.user.id, id=order_id)
    html = render_to_string('order_summary.html', {'order': order, "show_print_button": False})

    # Create an HttpResponse object with PDF content type and set filename
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="order_summary_{}.pdf"'.format(order_id)

    # Use WeasyPrint to generate PDF file from the HTML string and write to response object
    HTML(string=html).write_pdf(response)

    return response


@login_required
def cart_view(request):
    """
    View function that displays the user's cart with the ability to apply coupons to it.
    """
    # Retrieve or create the cart associated with the current user.
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Retrieve all coupons and exclude those that have already been used by the user
    coupons = Coupon.objects.all()
    unused_coupons = Coupon.objects.exclude(id__in=UsedCoupon.objects.filter(user=request.user, active=False).values('coupon_id'))

    # Create a form to apply coupons to the cart
    form = CouponApplyForm(request.POST or None)
    
    if form.is_valid():
        # If form is valid extract the coupon code entered by the user, retrieve a coupon with 
        # the entered code and check its validilty
        coupon_code = form.cleaned_data['code']
        try:
            coupon = Coupon.objects.get(code=coupon_code)
            user_coupon, created = UsedCoupon.objects.get_or_create(user=request.user, coupon=coupon)
            if user_coupon.active:
                cart.user_coupon = user_coupon
                cart.apply_coupon()
                messages.success(request, f"Coupon '{coupon_code}' applied successfully.")
            else:
                messages.error(request, f"Invalid coupon code '{coupon_code}'")
        except ObjectDoesNotExist:
            messages.error(request, f"Invalid coupon code '{coupon_code}'")
        return redirect('clothstore:cart')
    
    context = {'show_navbar_footer': True, 'cart': cart, 'unused_coupons': unused_coupons, 'coupon_form':form}
    return render(request, "cart.html", context=context)


@login_required
def update_cart_items(request, product_id, quantity):
    """
    View function that updates the quantity of a product in the user's cart or removes it from the cart entirely.

    Args: product_id: The ID of the product being updated.
          quantity: The new quantity of the product being updated, or None if the product is being removed from the cart.
    """
    # Retrieve the cart for the current user
    cart = get_object_or_404(Cart, user=request.user)

    # Get the product by ID or raise Http404 error if not found
    product = get_object_or_404(Product, id=product_id)

    # Retrieve the cart item for the product, if it exists
    cart_item = CartItem.objects.filter(cart__user=request.user, product=product).first()

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
    if cart.user_coupon:
        cart.apply_coupon()
        cart.save()

    return redirect('/clothstore/cart/')


@login_required
def apply_coupon(request, coupon_code):
    """
    Applies the given coupon to the user's cart and redirects to the cart page.
    
    Args: coupon_code: str representing the code of the coupon to apply
    """
    # Retrieve the user's cart
    cart = get_object_or_404(Cart, user=request.user)

    # Retrieve the coupon with the given code and apply to the user's cart
    coupon = get_object_or_404(Coupon, code=coupon_code)
    user_coupon, created = UsedCoupon.objects.get_or_create(user=request.user, coupon=coupon)
    cart.user_coupon = user_coupon
    cart.apply_coupon()
    messages.success(request, f"Coupon '{coupon}' applied successfully.")

    return redirect('/clothstore/cart/')


@login_required
def checkout(request):
    """
    View function to create a new order and save it to the database after checkout.
    """
    # Get the cart and the cart items for the current user
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = CartItem.objects.filter(cart__user=request.user)
    order_items = []

    # Create a billing address for the order using the user's profile
    billing_address = f"{request.user.profile.address}, {request.user.profile.city}, {request.user.profile.state}, {request.user.profile.country}, {request.user.profile.pin}"
        
    # Create a new order instance and save it to the database
    order = Order(cart=cart, user=request.user, billing_address=billing_address, contact=request.user.profile.contact, 
                  total_price=cart.total_price, discount=cart.discount, final_price=cart.final_price)
    if cart.user_coupon is not None:
        order.coupon = cart.user_coupon.coupon
    order.save()
    messages.success(request, f"Order placed successfully")

    # Create a list of order items and add them to the new order
    for item in cart_items:
        order_item = OrderItem(order=order, product=item.product,
                               quantity=item.quantity, final_item_price=item.final_item_price)
        order_items.append(order_item)
    OrderItem.objects.bulk_create(order_items)
            
    # Deactivate the used coupon, if any
    if cart.user_coupon:
        cart.user_coupon.active = False
        cart.user_coupon.save()

    # Delete cart items and update the cart's total price
    cart_items.delete()
    cart.update_total_price()

    return redirect("/clothstore/my_order/")


# Views for Product Admins
@login_required
@product_admin_required
def dashboard_view(request):
    """
    Renders the dashboard for the product admin.
    """
    context = {'show_navbar_footer': True}
    return render(request, "dashboard.html", context=context)


@login_required
@product_admin_required
def add_product_view(request):
    """
    View for product admin to add a new product to the store.
    """
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)

        # If form is valid, save the product and display success message. Else, display an error message.
        if form.is_valid():
            product = form.save(commit=False)
            product.product_admin = request.user
            product.save()
            messages.success(request, f"Product added successfully")
        else:
            messages.success(
                request, f"Invalid information! Please enter correct details")
    
    # Render product form if request method is not POST
    form = ProductForm()

    context = {'show_navbar_footer': True, "add_product_form": form}
    return render(request, "add_product.html", context=context)


@login_required
@product_admin_required
def view_products_view(request):
    """
    Display the details of an existing product for the logged-in product admin.
    """
    # Get all products associated with the logged in user that have a date less than or equal to the current date
    product_list = Product.objects.filter(product_admin=request.user.id, date__lte=datetime.date.today())
    
    context = {'show_navbar_footer': True, "product_list": product_list}
    return render(request, "view_products.html", context=context)


@login_required
@product_admin_required
def update_product_view(request, product_id):
    """
    Update the details of an existing product for the logged-in product admin.

    Args: product_id: ID of the product to be updated
    """
    # Retrieve the product object with the given ID, or raise a 404 error if it doesn't exist
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        form = ProductForm(request.POST or None, request.FILES or None, instance=product)
        
        # If the form data is valid, update the product object with the new details
        if form.is_valid():
            product = form.save(commit=False)
            product.product_admin = request.user
            if 'image' in request.FILES:
                product.image = request.FILES['image']
            product.save()
            messages.success(request, f"Product details updated successfully")
            return redirect("/clothstore/product_detail/" + str(product_id))
        else:
            messages.success(request, f"Invalid information! Please enter correct details")
    else:
        # If the request method is GET, display the form populated with existing product data
        form = ProductForm(instance=product)
    
    context = {'show_navbar_footer': True, "update_product_form": form} 
    return render(request, "update_product.html", context=context)


@login_required
@product_admin_required
def delete_product_view(request, product_id):
    """
    Deletes a specific product.

    Args: product_id: ID of the product to be deleted.
    """
    # Get the product by ID or raise Http404 error if not found
    product = get_object_or_404(Product, id=product_id)

    # If the request is a POST request, delete the product and redirect to the view_products page
    if request.method == "POST":
        product.delete()
        messages.success(request, f"Product deleted successfully")
        return redirect("/clothstore/view_products/")
    
    context = {'show_navbar_footer': True, "product": product}
    return render(request, "delete_product.html", context=context)