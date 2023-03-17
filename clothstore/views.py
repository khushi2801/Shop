from django.shortcuts import render, redirect, get_object_or_404
from clothstore.models import Product, UserProfile, Cart, Order, OrderItem
from .forms import UserForm, UserAuthenticationForm, ProductForm, UserUpdateForm, ProfileUpdateForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import re, datetime, json
from django.forms import model_to_dict
from decimal import Decimal
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.fields.files import ImageFieldFile


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
            print(messages)
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
        print(form.errors.as_json)
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
            print(request.FILES)
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
    print(product_data)
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
    

def buy_now_view(request, product_id):
    if request.method == 'POST':
        product = Product.objects.get(id=product_id)
        quantity = request.POST.get('quantity')
        order_total = product.price * int(quantity)
        Order.objects.create(user=request.user, product=product, quantity=quantity, order_total=order_total)
        # cart_items = request.session.get('cart_items', [])
        # cart_items.append(product_id)
        # request.session['cart_items'] = cart_items
        return redirect('/clothstore/my_order')
    else:
        product = Product.objects.get(id=product_id)
        return render(request, 'buy_now.html', {'product': product})


# View for displaying orders
@login_required
def my_order_view(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, "my_order.html", {"orders": orders})


@login_required
def cancel_order(request):
    orders = Order.objects.filter(user=request.user)
    orders.delete()
    print(orders)
    return render(request, "my_order.html", {"orders": orders})


# View for displaying cart items
@login_required
def cart_view(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_cart_price = sum(item.final_item_price for item in cart_items)
    return render(request, "cart.html", {'cart_items': cart_items, 'total_cart_price': total_cart_price})


@login_required
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)
    order_items = []
    total_order_price = 0
    for item in cart_items:
        final_item_price = item.product.price*item.quantity
        total_order_price += final_item_price
    order = Order(user=request.user, total_price=total_order_price)
    order.save()
    for item in cart_items:
        final_item_price = item.product.price*item.quantity
        order_item = OrderItem(order=order, product=item.product, quantity=item.quantity, final_item_price=final_item_price)
        order_items.append(order_item) 
    OrderItem.objects.bulk_create(order_items)
    cart_items.delete()
    return redirect("/clothstore/home/")