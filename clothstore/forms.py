from django import forms
from django.contrib.auth.forms import UserCreationForm
from phonenumber_field.formfields import PhoneNumberField
from .models import MyUser, Product, UserProfile


# Choices for User Type field in UserForm
USER_TYPE_CHOICES = (
    ('Customer', 'Customer'), 
    ('ProductAdmin', 'Product Admin'),
    )


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


class UserForm(UserCreationForm):
    """
    A form that inherits from Django's built-in UserCreationForm and adds additional fields for creating a new user.

    Attributes:
        user_type: CharField - The user's type
        name: CharField - The user's name
        email: EmailField - The user's email address
        password1: CharField - The user's password
        password2: CharField - The user's confirmed password

    Meta:
        model: MyUser - The model that the form corresponds to
        fields: list - The fields to include in the form

    Methods:
        clean(): A validation function that cleans and validates the form data
    """
    user_type = forms.ChoiceField(required=True, widget=forms.RadioSelect(), choices=USER_TYPE_CHOICES)
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'autofocus':'autofocus', 'placeholder': 'Enter your name'}))
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'}))
    
    class Meta:
        model = MyUser
        fields = ['user_type', 'name', 'email', 'password1', 'password2']

    def clean(self):
        super(UserForm, self).clean()
        email = self.cleaned_data.get('email')
        return self.cleaned_data


class UserAuthenticationForm(forms.Form):
    """
    A form to authenticate a user. This form accepts email and password for authentication.

    Attributes:
        email: EmailField - The user's email address
        password: CharField - The user's password
    """
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter password'}))


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


class UserUpdateForm(forms.ModelForm):
    """
    A form for updating user information. This form accepts user's name and email.

    Attributes:
        name: CharField - The user's name
        email: EmailField - The user's email address

    Meta:
        model: MyUser - The model that the form corresponds to
        fields: list - The fields to include in the form
    """
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'autofocus':'autofocus', 'placeholder': 'Enter your name'}))
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}))

    class Meta:
        model = MyUser
        fields = ['name', 'email']


class ProfileUpdateForm(forms.ModelForm):
    """
    A form for updating user's profile details. This form accepts user's date of birth, address, city, country, 
    state, contact, pin, and image.

    Attributes:
        dob: DateField - The user's date of birth
        address: CharField - The user's street address
        city: CharField - The user's city
        country: CharField - The user's country
        state: CharField - The user's state
        contact: PhoneNumberField - The user's phone number
        pin: CharField - The user's postal code
        image: ImageField - An image of the user

    Meta:
        model: UserProfile - The model that the form corresponds to
        fields: list - The fields to include in the form
    """
    dob = forms.DateField(label="Date of Birth", widget=forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Enter Date of Birth'}))
    address = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter address'}))
    city = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter city'}))
    country = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter country'}))
    state = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter state'}))
    contact = PhoneNumberField(region="IN", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}))
    pin = forms.CharField(widget=forms.TimeInput(attrs={'class': 'form-control', 'placeholder': 'Enter pincode'}))
    image = forms.ImageField(widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'placeholder': 'Upload Image'}))

    class Meta:
        model = UserProfile
        fields = ['dob', 'address', 'city', 'state', 'country', 'contact', 'pin', 'image']


class CouponApplyForm(forms.Form):
    """
    A form for applying coupon to cart. This form accepts coupon code.

    Attributes:
        code: CharField - The code given by user
    """
    code = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Coupon Code'}))