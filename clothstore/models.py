from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
import datetime, decimal
from django.conf import settings
from phonenumber_field.modelfields import PhoneNumberField
from django.core.validators import MinValueValidator, MaxValueValidator


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


# Model for storing user data
class MyUser(AbstractUser):
    user_type = models.CharField(max_length=20)
    username = None # Removing username field as Email is used as unique identifier
    name = models.CharField(max_length=50, null=False)
    email = models.EmailField(unique=True, null=False)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']


# Model for storing products added by product admin
class Product(models.Model):
    product_admin = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    category = models.CharField(max_length=20, null=False)
    name = models.CharField(max_length=50, null=False)
    brand = models.CharField(max_length=50, null=False)
    size = models.CharField(max_length=5, null=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    image = models.ImageField(upload_to='images/', null=False)
    date = models.DateField(default=datetime.date.today)

    def order_quantity(self):
        order_items = OrderItem.objects.filter(product=self)
        return sum(order_item.quantity for order_item in order_items)

    def __str__(self):
        return self.name


# Model for storing additional user data
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


# Model for storing all type od coupons
class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    amount = models.IntegerField(null=True, blank=True)
    percentage = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    def __str__(self):
        return self.code


# Model for storing user specific coupons and details
class UsedCoupon(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)


# Model for storing cart data
class Cart(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    user_coupon = models.ForeignKey(UsedCoupon, on_delete=models.SET_NULL, null=True, blank=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    final_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    checked_out = models.BooleanField(default=False)

    def update_total_price(self):
        """
        Update the total cart price based on the sum of all the cart items' final prices.
        """
        self.total_price = sum(item.final_item_price for item in self.cart_items.all())
        if not self.total_price:
            self.user_coupon = None
            self.discount = 0
        self.save()

    def apply_coupon(self):
        if self.user_coupon.coupon.amount:
            self.discount = self.user_coupon.coupon.amount
        if self.user_coupon.coupon.percentage:
            self.discount = self.total_price * self.user_coupon.coupon.percentage / 100
        self.update_total_price()

    def save(self, *args, **kwargs):
        if self.pk is not None:
            self.final_price = self.total_price - decimal.Decimal(str(self.discount))
        super(Cart, self).save(*args, **kwargs)

    def __str__(self):
        return self.user.email


# Model for storing cart items
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    final_item_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


# Model for storing user order data
class Order(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    billing_address = models.CharField(max_length=150, null=True, blank=True)
    contact = PhoneNumberField(null=True, blank=True)
    items = models.ManyToManyField(Product, through='OrderItem', related_name='orders')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    discount = models.DecimalField(default=0.00, decimal_places=2, max_digits=10)
    final_price = models.DecimalField(default=0.00, decimal_places=2, max_digits=10)
    is_paid = models.BooleanField(default=False)    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)
    
    def __str__(self):
        return self.user.email


# Model for storing item data of an order
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    final_item_price = models.DecimalField(max_digits=10, decimal_places=2, null=False)