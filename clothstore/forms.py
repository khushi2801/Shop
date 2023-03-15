from django import forms
from .models import MyUser, Product, UserProfile
from django.contrib.auth.forms import UserCreationForm
from phonenumber_field.formfields import PhoneNumberField
# from bootstrap_datepicker_plus import DatePickerInput

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


# Form to take user details during signup
class UserForm(UserCreationForm):
    user_type = forms.ChoiceField(required=True, widget=forms.RadioSelect(attrs={'class': 'no-bullets'}), choices=USER_TYPE_CHOICES)
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'autofocus':'autofocus', 'placeholder': 'Enter your name'}))
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'}))
    
    class Meta:
        model = MyUser
        fields = ['user_type', 'name', 'email', 'password1', 'password2']

    # Clean Validation Function
    def clean(self):
        super(UserForm, self).clean()       # Data from the Form is fetched using super function
        email = self.cleaned_data.get('email')
        return self.cleaned_data


# Form to take user details during login
class UserAuthenticationForm(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter password'}))


# Form to take product details during add and update product
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


# Form to take user details during profile update
class UserUpdateForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'autofocus':'autofocus', 'placeholder': 'Enter your name'}))
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}))

    class Meta:
        model = MyUser
        fields = ['name', 'email']


# Form to take user additional details during profile update
class ProfileUpdateForm(forms.ModelForm):
    dob = forms.DateField(label="Date of Birth", widget=forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Enter Date of Birth'}))
    address = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter address'}))
    city = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter city'}))
    country = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter country'}))
    contact = PhoneNumberField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter phone number'}))
    pin = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter pincode'}))
    image = forms.ImageField(widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'placeholder': 'Upload Image'}))

    class Meta:
        model = UserProfile
        fields = ['dob', 'address', 'city', 'country', 'contact', 'pin', 'image']