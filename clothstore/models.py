from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
import datetime
from django.conf import settings
from phonenumber_field.modelfields import PhoneNumberField  


class MyUserManager(UserManager):
    def create_user(self, name, email, password=None, **kwargs):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(name=name, email=self.normalize_email(email), **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, name, email, password, **kwargs):
        kwargs.setdefault('is_staff', True)
        kwargs.setdefault('is_superuser', True)
        
        return self.create_user(name, email, password, **kwargs)

class MyUser(AbstractUser):
    user_type = models.CharField(max_length=20)
    username = None # Removing username field as Email is used as unique identifier
    name = models.CharField(max_length=50, null=False)
    email = models.EmailField(unique=True, null=False)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    
class Product(models.Model):
    product_admin = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    category = models.CharField(max_length=20, null=False)
    name = models.CharField(max_length=50, null=False)
    brand = models.CharField(max_length=50, null=False)
    size = models.CharField(max_length=5, null=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    image = models.ImageField(upload_to='images/', null=False)
    date = models.DateField(default=datetime.date.today)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE, related_name='profile')
    dob = models.DateField(null=True)
    address = models.CharField(max_length=150, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    state = models.CharField(max_length=50, null=True, blank=True)
    country = models.CharField(max_length=50, null=True, blank=True)
    contact = PhoneNumberField(unique=True, null=True, blank=True)
    pin = models.PositiveIntegerField(null=True, blank=True)
    image = models.ImageField(upload_to='profile_images/', default='profile.png', null=True, blank=True)


class Order(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    items = models.ManyToManyField(Product, through='OrderItem', related_name='orders')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)
    billing_address = models.CharField(max_length=150, null=True, blank=True)
    contact = PhoneNumberField(null=True, blank=True)

    # discount = models.DecimalField(default=0.00, decimal_places=2, max_digits=10)
    # final_price = models.DecimalField(default=0.00, decimal_places=2, max_digits=10)
    # is_paid = models.BooleanField(default=True)    
    # order_total = models.DecimalField(max_digits=10, decimal_places=2)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    final_item_price = models.DecimalField(max_digits=10, decimal_places=2, null=False)


class Cart(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    final_item_price = models.DecimalField(max_digits=10, decimal_places=2, null=False)


# class CartItem(models.Model):
#     user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     quantity = models.PositiveIntegerField(default=1)
#     final_item_price = models.DecimalField(max_digits=10, decimal_places=2, null=False)