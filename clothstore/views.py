from django.shortcuts import render, redirect, get_object_or_404
from clothstore.models import Product, Cart, Order, OrderItem
from .forms import UserForm, UserAuthenticationForm, ProductForm, UserUpdateForm, ProfileUpdateForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import re, datetime, json
from django.forms import model_to_dict
from decimal import Decimal
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.fields.files import ImageFieldFile
from django.http import HttpResponse
from weasyprint import HTML
from django.template.loader import render_to_string


# View for user and product admin signup
def signup_view(request):
    error_list = []
    if request.method == "POST":
        form = UserForm(request.POST)
        error_list = re.sub(r'\*\s*(password2|email)\n',
                            '', form.errors.as_text())
        error_list = list(re.sub(r'\*.*?', '', error_list).split("\n"))
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
                return redirect("/clothstore/home")
        else:
            messages.error(request, "Invalid information!")
    form = UserForm()
    return render(request, "signup.html", {"signup_form": form, "error_list": error_list})


# View for user and product admin login
def login_view(request):
    if request.method == "POST":
        form = UserAuthenticationForm(request.POST)
        if form.is_valid():
            user = authenticate(
                email=form.cleaned_data['email'], password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                messages.info(request, f"Welcome {user.name}")
                if user.user_type == "ProductAdmin":
                    return redirect("/clothstore/dashboard/")
                else:
                    return redirect("/clothstore/home/")
            else:
                messages.error(request, "Invalid email or password")
        else:
            messages.error(request, "Invalid email or password")
    form = UserAuthenticationForm()
    return render(request, "login.html", {"login_form": form})


# View for user and product admin logout
@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have successfully logged out")
    form = UserAuthenticationForm()
    return redirect("/clothstore/login")


# View for displaying profile details
@login_required
def profile_view(request):    
    user_data = model_to_dict(request.user.profile)
    return render(request, "profile.html", {"user_data": user_data})


# View for updating product detail
@login_required
def update_profile_view(request):
    if request.method == "POST":
        u_form = UserUpdateForm(request.POST or None, request.FILES or None, instance=request.user)
        p_form = ProfileUpdateForm(request.POST or None, request.FILES or None, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f"Profile details updated successfully")
            return redirect("/clothstore/profile/")
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    return render(request, "update_profile.html", {"user_update_form": u_form, "profile_update_form": p_form})


# Product Admin side
# Dashboard view
@login_required
def dashboard_view(request):
    return render(request, "dashboard.html")

class CustomJSONEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        elif isinstance(obj, ImageFieldFile):
            try:
                return obj.url
            except ValueError:
                return ""
        return super().default(obj)


# View for adding product
@login_required
def add_product_view(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.product_admin = request.user
            product.save()
            messages.success(request, f"Product added successfully")
        else:
            messages.success(
                request, f"Invalid information! Please enter correct details")
    form = ProductForm()
    return render(request, "add_product.html", {"add_product_form": form})


# View for displaying list of products
@login_required
def view_products_view(request):
    product_list = Product.objects.filter(product_admin = request.user.id, date__lte=datetime.date.today())
    return render(request, "view_products.html", {"product_list": product_list})


# View for displaying product detail
@login_required
def product_detail_view(request, product_id):
    p = Product.objects.get(id=product_id)
    product = model_to_dict(p)
    return render(request, "product_detail.html", {"product": product})


# View for updating product detail
@login_required
def update_product_view(request, product_id):
    obj = get_object_or_404(Product, id=product_id)
    if request.method == "POST":
        form = ProductForm(request.POST or None, request.FILES or None, instance=obj)
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
        form = ProductForm(instance=obj)
    product_data = json.dumps(model_to_dict(obj), cls=CustomJSONEncoder)
    return render(request, "update_product.html", {"update_product_form": form, "product_data": product_data})


# View for deleting product
@login_required
def delete_product_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == "POST":
        product.delete()
        messages.success(request, f"Product deleted successfully")
        return redirect("/clothstore/view_products/")
    return render(request, "delete_product.html", {"product": product})



# Customer side
# Home view
@login_required
def home_view(request):
    product_list = Product.objects.all()
    return render(request, "home.html", {"product_list": product_list})


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item = Cart.objects.filter(user=request.user, product=product).first()     # Check if the user already has this product in their cart
    if cart_item:
        cart_item.quantity += 1
        cart_item.final_item_price += product.price
        cart_item.save()
        messages.success(request, f"{product.name} added to cart")
    else:
        new_cart_item = Cart(user=request.user, product=product, quantity=1, final_item_price=product.price)
        new_cart_item.save()
        messages.success(request, f"{product.name} added to cart")
    return redirect('/clothstore/home/')
    

# View for adding product to cart and moving to cart view
@login_required
def buy_now(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item = Cart.objects.filter(user=request.user, product=product).first()     # Check if the user already has this product in their cart
    if cart_item:
        cart_item.quantity += 1
        cart_item.final_item_price += product.price
        cart_item.save()
        messages.success(request, f"{product.name} added to cart")
    else:
        new_cart_item = Cart(user=request.user, product=product, quantity=1, final_item_price=product.price)
        new_cart_item.save()
        messages.success(request, f"{product.name} added to cart")
    return redirect('/clothstore/cart/')


# View for displaying orders
@login_required
def my_order_view(request):
    active_orders = Order.objects.filter(user=request.user, status=True)
    cancel_orders = Order.objects.filter(user=request.user, status=False)
    return render(request, "my_order.html", {"active_orders": active_orders, "cancel_orders": cancel_orders})


# View for cancelling order
@login_required
def order_operations(request, order_id):
    order = Order.objects.get(user=request.user, id=order_id)
    if 'order_summary' in request.path_info:
        return render(request, "order_summary.html", {"order": order, "show_print_button": True})
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
    order = Order.objects.get(user=request.user.id, id=order_id)      # Get the order object using the order_id
    html = render_to_string('order_summary.html', {'order': order, "show_print_button": False})     # Render the template with the order data
    response = HttpResponse(content_type='application/pdf')     # Create a HttpResponse object with PDF mime type
    response['Content-Disposition'] = 'filename="order_summary_{}.pdf"'.format(order_id)
    HTML(string=html).write_pdf(response)      # Use WeasyPrint to convert HTML to PDF
    return response


# View for displaying cart items
@login_required
def cart_view(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_cart_price = sum(item.final_item_price for item in cart_items)
    return render(request, "cart.html", {'cart_items': cart_items, 'total_cart_price': total_cart_price})


# View for updating cart items
@login_required
def update_cart_items(request, product_id, quantity):
    product = get_object_or_404(Product, id=product_id)
    item = Cart.objects.filter(user=request.user, product=product).first()
    if item and quantity:
        item.quantity = quantity
        item.final_item_price = product.price * quantity
        item.save()
    elif not quantity:
        item.delete()
    return redirect('/clothstore/cart/')


# View for checkout items from cart
@login_required
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)
    order_items = []
    total_order_price = 0
    for item in cart_items:
        final_item_price = item.product.price*item.quantity
        total_order_price += final_item_price
    billing_address = f"{request.user.profile.address}, {request.user.profile.city}, {request.user.profile.state}, {request.user.profile.country}, {request.user.profile.pin}"
    order = Order(user=request.user, total_price=total_order_price, billing_address=billing_address, contact=request.user.profile.contact)
    order.save()
    messages.success(request, f"Order placed successfully")
    for item in cart_items:
        final_item_price = item.product.price*item.quantity
        order_item = OrderItem(order=order, product=item.product, quantity=item.quantity, final_item_price=final_item_price)
        order_items.append(order_item) 
    OrderItem.objects.bulk_create(order_items)
    cart_items.delete()
    return redirect("/clothstore/home/")