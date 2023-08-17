import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.forms import model_to_dict
from django.shortcuts import get_object_or_404, redirect, render
from .models import Product
from .decorators import seller_required
from .forms import ProductForm


@login_required
def product_detail(request, product_id):
    """
    Renders the product detail page for a given product.

    Args: product_id: ID of the product to display
    """
    # Get the product with the given ID and convert the product object to a dictionary to pass to the template
    p = Product.objects.get(id=product_id)
    product = model_to_dict(p)
    
    context = {'show_navbar_footer': True, "product": product}
    return render(request, 'clothes/product_detail.html', context)



@login_required
@seller_required
def add_product(request):
    """
    View for merchant to add a new product to the store.
    """
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)

        # If form is valid, save the product and display success message. Else, display an error message.
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            messages.success(request, f"Product added successfully")
        else:
            messages.success(
                request, f"Invalid information! Please enter correct details")
    
    # Render product form if request method is not POST
    form = ProductForm()

    context = {'show_navbar_footer': True, "add_product_form": form}
    return render(request, 'clothes/add_product.html', context)


@login_required
@seller_required
def view_products(request):
    """
    Display the details of an existing product for the logged-in merchant.
    """
    # Get all products associated with the logged in user that have a date less than or equal to the current date
    product_list = Product.objects.filter(seller=request.user.id, date__lte=datetime.date.today())
    
    context = {'show_navbar_footer': True, "product_list": product_list}
    return render(request, 'clothes/view_products.html', context)


@login_required
@seller_required
def update_product(request, product_id):
    """
    Update the details of an existing product for the logged-in merchant.

    Args: product_id: ID of the product to be updated
    """
    # Retrieve the product object with the given ID, or raise a 404 error if it doesn't exist
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        form = ProductForm(request.POST or None, request.FILES or None, instance=product)
        
        # If the form data is valid, update the product object with the new details
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            if 'image' in request.FILES:
                product.image = request.FILES['image']
            product.save()
            messages.success(request, f"Product details updated successfully")
            return redirect("/clothes/product_detail/" + str(product_id))
        else:
            messages.success(request, f"Invalid information! Please enter correct details")
    else:
        # If the request method is GET, display the form populated with existing product data
        form = ProductForm(instance=product)
    
    context = {'show_navbar_footer': True, "update_product_form": form} 
    return render(request, 'clothes/update_product.html', context)


@login_required
@seller_required
def delete_product(request, product_id):
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
        return redirect("/clothes/view_products/")
    
    context = {'show_navbar_footer': True, "product": product}
    return render(request, 'clothes/delete_product.html', context)