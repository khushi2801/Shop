from django.shortcuts import render, redirect, get_object_or_404
from clothstore.models import Product, Cart, CartItem, Order, OrderItem, Coupon, UsedCoupon
from .forms import UserForm, UserAuthenticationForm, ProductForm, UserUpdateForm, ProfileUpdateForm, CouponApplyForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import re, datetime
from django.forms import model_to_dict
from django.http import HttpResponse
from weasyprint import HTML
from django.template.loader import render_to_string
from .decorators import product_admin_required


# View for user and product admin signup
def signup_view(request):
    error_list = []

    # If UserForm is submitted check for form validity
    if request.method == "POST":
        form = UserForm(request.POST)

        # Store errors to displays if form is invalid
        error_list = re.sub(r'\*\s*(password2|email)\n',
                            '', form.errors.as_text())
        error_list = list(re.sub(r'\*.*?', '', error_list).split("\n"))

        # If form is valid, create user, authenticate user and login else print message
        if form.is_valid():
            form.save()
            messages.success(request, f"Account created successfully")
            user = authenticate(
                email=form.cleaned_data['email'], password=form.cleaned_data['password1'])
            login(request, user)
            messages.success(request, f"Welcome {user.name}")
            if form.cleaned_data['user_type'] == "ProductAdmin":
                return redirect("/clothstore/dashboard")
            else:
                return redirect("/")
        else:
            messages.error(request, "Invalid information!")
    
    form = UserForm()
    context = {"signup_form": form, "error_list": error_list}
    return render(request, "signup.html", context=context)


# View for user and product admin login
def login_view(request):
    # If UserAuthenticationForm is submitted check for form validity
    if request.method == "POST":
        form = UserAuthenticationForm(request.POST)

        # If form is valid authenticate user else print message
        if form.is_valid():
            user = authenticate(
                email=form.cleaned_data['email'], password=form.cleaned_data['password'])
            
            # If user is authenticated login else print message
            if user is not None:
                login(request, user)
                messages.info(request, f"Welcome {user.name}")

                # If user is product admin redirect to dashboard and redirect to home if user is customer
                if user.user_type == "ProductAdmin":
                    return redirect("/clothstore/dashboard/")
                else:
                    return redirect("/")
            else:
                messages.error(request, "Invalid email or password")
        else:
            messages.error(request, "Invalid email or password")

    form = UserAuthenticationForm()
    context = {"login_form": form}
    return render(request, "login.html", context=context)


# View for user and product admin logout
@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have successfully logged out")
    return redirect("/")


# View for displaying profile details
@login_required
def profile_view(request):
    # Convert object to dictionary to pass to html
    user_data = model_to_dict(request.user.profile)

    context = {"user_data": user_data}
    return render(request, "profile.html", context=context)


# View for updating product detail
@login_required
def update_profile_view(request):
    # If form is submitted check for form validity
    if request.method == "POST":
        # UserUpdateForm for taking user basic details
        u_form = UserUpdateForm(request.POST or None,
                                request.FILES or None, instance=request.user)
        
        # ProfileUpdateForm for taking user additional details
        p_form = ProfileUpdateForm(
            request.POST or None, request.FILES or None, instance=request.user.profile)
        
        # If form is valid save updated details and redirect to product details page else print message
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f"Profile details updated successfully")
            return redirect("/clothstore/profile/")
    else:
        # Else populate UserUpdateForm and ProfileUpdateForm with existing product data
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    
    context =  {"user_update_form": u_form, "profile_update_form": p_form}
    return render(request, "update_profile.html", context=context)


# Product Admin side
# Dashboard view
@login_required
@product_admin_required
def dashboard_view(request):
    return render(request, "dashboard.html")


# View for adding product
@login_required
@product_admin_required
def add_product_view(request):
    # If form is submitted check for form validity
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)

        # If form is valid add product else print message
        if form.is_valid():
            product = form.save(commit=False)
            product.product_admin = request.user
            product.save()
            messages.success(request, f"Product added successfully")
        else:
            messages.success(
                request, f"Invalid information! Please enter correct details")
    
    # Form for taking product details
    form = ProductForm()

    context = {"add_product_form": form}
    return render(request, "add_product.html", context=context)


# View for displaying list of products
@login_required
@product_admin_required
def view_products_view(request):
    # Get all products
    product_list = Product.objects.filter(
        product_admin=request.user.id, date__lte=datetime.date.today())
    
    context = {"product_list": product_list}
    return render(request, "view_products.html", context=context)


# View for displaying product detail
@login_required
@product_admin_required
def product_detail_view(request, product_id):
    # Get product
    p = Product.objects.get(id=product_id)

    # Convert object to dictionary to pass to html
    product = model_to_dict(p)

    context = {"product": product}
    return render(request, "product_detail.html", context=context)


# View for updating product detail
@login_required
@product_admin_required
def update_product_view(request, product_id):
    # Get product
    product = get_object_or_404(Product, id=product_id)

    # If form is submitted check for form validity
    if request.method == "POST":
        form = ProductForm(request.POST or None,
                           request.FILES or None, instance=product)
        
        # If form is valid save updated details and redirect to product details page else print message
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
        # Else populate form with existing product data
        form = ProductForm(instance=product)
    
    context = {"update_product_form": form} 
    return render(request, "update_product.html", context=context)


# View for deleting product
@login_required
@product_admin_required
def delete_product_view(request, product_id):
    # Get product
    product = get_object_or_404(Product, id=product_id)

    # Delete product when confirmed
    if request.method == "POST":
        product.delete()
        messages.success(request, f"Product deleted successfully")
        return redirect("/clothstore/view_products/")
    
    context = {"product": product}
    return render(request, "delete_product.html", context=context)


# Customer side
# Home view
# @login_required
def home_view(request):
    # Get all products
    product_list = Product.objects.all()
    context = {"product_list": product_list}
    return render(request, "home.html", context=context)


# View for adding product to cart
@login_required
def add_to_cart(request, product_id):
    # Get product and create cart if not created
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Add product as cart item or increase its quantity if already added
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not item_created:
        cart_item.quantity += 1

    # Update price of cart item as well as cart
    cart_item.final_item_price = cart_item.quantity * product.price
    cart_item.save()
    cart.update_total_price()
    messages.success(request, f"{product.name} added to cart")

    return redirect('/clothstore/home/')


# View for adding product to cart and redirecting to cart view
@login_required
def buy_now(request, product_id):
    # Get product and create cart if not created
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Add product as cart item or increase its quantity if already added
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not item_created:
        cart_item.quantity += 1
    
    # Update price of cart item as well as cart
    cart_item.final_item_price = cart_item.quantity * product.price
    cart_item.save()
    cart.update_total_price()
    messages.success(request, f"{product.name} added to cart")

    return redirect('/clothstore/cart/')


# View for displaying orders
@login_required
def my_order_view(request):
    # Get active orders of user
    active_orders = Order.objects.filter(user=request.user, status=True)

    # Get cancelled order of user
    cancelled_orders = Order.objects.filter(user=request.user, status=False)

    context = {"active_orders": active_orders, "cancelled_orders": cancelled_orders}
    return render(request, "my_order.html", context=context)


# View for cancelling order
@login_required
def order_operations(request, order_id):
    # Get order
    order = Order.objects.get(user=request.user, id=order_id)

    if 'order_summary' in request.path_info:
        context = {"order": order, "show_print_button": True}
        return render(request, "order_summary.html", context=context)
    elif 'cancel_order' in request.path_info:
        # Handle the case where the order doesn't exist
        if order.status:
            order.status = False
            order.save()
            messages.success(request, f"Order Cancelled")
    
    return redirect('/clothstore/my_order/')


# View for generating order summary pdf
@login_required
def generate_pdf(request, order_id):
    # Get the order object using the order_id
    order = Order.objects.get(user=request.user.id, id=order_id)

    # Render the template with the order data
    html = render_to_string('order_summary.html', {'order': order, "show_print_button": False})

    # Create a HttpResponse object with PDF mime type
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="order_summary_{}.pdf"'.format(order_id)

    # Use WeasyPrint to convert HTML to PDF
    HTML(string=html).write_pdf(response)

    return response


# View for displaying cart items
@login_required
def cart_view(request):
    print("yes")
    # Get user cart and coupons available
    cart, created = Cart.objects.get_or_create(user=request.user)
    coupons = Coupon.objects.all()
    unused_coupons = Coupon.objects.exclude(id__in=UsedCoupon.objects.filter(user=request.user, active=False).values('coupon_id'))

    # Form for taking coupon code
    form = CouponApplyForm(request.POST or None)
    
    if form.is_valid():
        # If form is valid take coupon code
        coupon_code = form.cleaned_data['code']

        # Get or create UsedCoupon if Coupon does not exist and apply to cart else print message for invalid code
        try:
            coupon = Coupon.objects.get(code=coupon_code)
            user_coupon, created = UsedCoupon.objects.get_or_create(user=request.user, coupon=coupon)
            if user_coupon.active:
                cart.user_coupon = user_coupon
                cart.apply_coupon()
                messages.success(request, f"Coupon '{coupon_code}' applied successfully.")
            else:
                messages.error(request, f"Invalid coupon code '{coupon_code}'")
        except UsedCoupon.DoesNotExist:
            messages.error(request, f"Invalid coupon code '{coupon_code}'")
        
        return redirect('clothstore:cart')
    
    context = {'cart': cart, 'unused_coupons': unused_coupons, 'coupon_form':form}
    return render(request, "cart.html", context=context)


# View for updating cart items
@login_required
def update_cart_items(request, product_id, quantity):
    # Get user cart, cart item whose quantity needs to be updated
    cart = get_object_or_404(Cart, user=request.user)
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.filter(cart__user=request.user, product=product).first()

    # Change quantity as passed in url or delete item if quantity = 0
    if cart_item and quantity:
        cart_item.quantity = quantity
        cart_item.final_item_price = product.price * quantity
        cart_item.save()
    elif not quantity:
        cart_item.delete()

    
    # Update total price
    cart.update_total_price()

    # Update coupon discount id added
    if cart.user_coupon:
        cart.apply_coupon()
        cart.save()

    return redirect('/clothstore/cart/')


# View for applying coupon code
@login_required
def apply_coupon(request, coupon_code):
    # Get user cart
    cart = get_object_or_404(Cart, user=request.user)

    # Get coupon object if coupon_code is valid
    coupon = get_object_or_404(Coupon, code=coupon_code)
    user_coupon, created = UsedCoupon.objects.get_or_create(user=request.user, coupon=coupon)

    # Apply to cart
    cart.user_coupon = user_coupon
    cart.apply_coupon()
    messages.success(request, f"Coupon '{coupon}' applied successfully.")

    return redirect('/clothstore/cart/')


# View for checkout items from cart
@login_required
def checkout(request):
    # Get cart amd cart items of user
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = CartItem.objects.filter(cart__user=request.user)
    order_items = []

    # Get billing address from user profile
    billing_address = f"{request.user.profile.address}, {request.user.profile.city}, {request.user.profile.state}, {request.user.profile.country}, {request.user.profile.pin}"
        
    # Create and save order
    order = Order(cart=cart, user=request.user, billing_address=billing_address, contact=request.user.profile.contact, 
                  total_price=cart.total_price, discount=cart.discount, final_price=cart.final_price)
    if cart.user_coupon is not None:
        order.coupon = cart.user_coupon.coupon
    order.save()
    messages.success(request, f"Order placed successfully")

    # Create order item objects
    for item in cart_items:
        order_item = OrderItem(order=order, product=item.product,
                               quantity=item.quantity, final_item_price=item.final_item_price)
        order_items.append(order_item)
    OrderItem.objects.bulk_create(order_items)
            
    # If coupon is used make it inactive
    if cart.user_coupon:
        cart.user_coupon.active = False
        cart.user_coupon.save()

    # Remove cart items and update cart price
    cart_items.delete()
    cart.update_total_price()

    return redirect("/clothstore/my_order/")