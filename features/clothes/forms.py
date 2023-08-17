from django import forms
from .models import Product


# Choices for Product Category field in ProductForm
PRODUCT_CATEGORY_CHOICES = (
    ('Tops', 'Tops'),
    ('Shirts', 'Shirts'),
    ('Trousers', 'Trousers'),
    ('Jeans', 'Jeans'),
    )


# Choices for Product Size field in ProductForm
PRODUCT_SIZE_CHOICES = (
    ('XS', 'XS'),
    ('S', 'S'), 
    ('L', 'L'),
    ('XL', 'XL'), 
    ('XXL', 'XXL'),
    )


class ProductForm(forms.ModelForm):
    """
    A form for adding and updating product details. This form accepts product category, name, brand, size, price, and image.

    Attributes:
        category: ChoiceField - The product's category
        name: CharField - The name of the product
        brand: CharField - The brand of the product
        size: ChoiceField - The size of the product
        price: NumberInput - The price of the product
        image: ClearableFileInput - An image of the product

    Meta:
        model: Product - The model that the form corresponds to
        fields: list - The fields to include in the form
        widgets: dict - The widgets to use for each field
    """
    class Meta:
        model = Product
        fields = ['category', 'name', 'brand', 'size', 'price', 'image']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select category'}, choices=PRODUCT_CATEGORY_CHOICES),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter product name'}),
            'brand': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter brand name'}),
            'size': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Select size'}, choices=PRODUCT_SIZE_CHOICES),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter price'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control', 'placeholder': 'Upload Image'}),
        }