from django.shortcuts import render, redirect, get_object_or_404
from clothstore.models import Product, UserProfile
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
        error_list = re.sub(r'\*\s*(__all__)\n', '', form.errors.as_text())
        error_list = list(re.sub(r'\*.*?', '', error_list).split("\n"))
        if form.is_valid():
            user = authenticate(
                email=form.cleaned_data['email'], password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                messages.info(request, f"Welcome {user.name}")
                if user.user_type == "productAdmin":
                    return redirect("/clothstore/dashboard/")
                    # return redirect("/clothstore/dashboard/" + user.name)
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
    # u = UserProfile.objects.get(id=request.user.id)
    
    user_data = model_to_dict(request.user.profile)
    print(user_data)
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
def home_view(request):
    return render(request, "home.html")