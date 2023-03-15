from django import forms
from .models import myUser, Product
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

USER_TYPE_CHOICES = (
    ('customer', 'Customer'), 
    ('productAdmin', 'Product Admin'),
    )

PRODUCT_CATEGORY_CHOICES = (
    ('tops', 'Tops'),
    ('shirts', 'Shirts'),
    ('trousers', 'Trousers'),
    ('jeans', 'Jeans'),
    )

PRODUCT_SIZE_CHOICES = (
    ('xs', 'XS'),
    ('s', 'S'), 
    ('l', 'L'),
    ('xl', 'XL'), 
    ('xxl', 'XXL'),
    )


class UserForm(UserCreationForm):

    user_type = forms.ChoiceField(required=True, widget=forms.RadioSelect(attrs={'class': 'no-bullets'}), choices=USER_TYPE_CHOICES)
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'autofocus':'autofocus', 'placeholder': 'Enter your name'}))
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'}))
    
    class Meta:
        model = myUser
        fields = ['user_type', 'name', 'email', 'password1', 'password2']

    # Clean Validation Function
    def clean(self):
        super(UserForm, self).clean()       # Data from the Form is fetched using super function
        email = self.cleaned_data.get('email')
        return self.cleaned_data


class UserAuthenticationForm(forms.Form):

    email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter password'}))


class ProductForm(forms.ModelForm):    

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