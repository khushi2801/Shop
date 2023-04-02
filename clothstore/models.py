import datetime
import decimal
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class MyUserManager(UserManager):
    """
    Custom manager for the MyUser model that overrides the create_user() and create_superuser() methods
    to accept a name, email, and password, and set up a new user with those details. The email field is
    used as the unique identifier instead of the default username field. The create_superuser() method
    also sets the is_staff and is_superuser flags to True.

    Methods:
        create_user(name, email, password, **kwargs): Creates a new user with the given name, email, and 
            password, and saves it to the database.
        create_superuser(name, email, password, **kwargs): Creates a new superuser with the given name, 
            email, and password, and saves it to the database.
    """
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
    """
    A custom user model which uses email as the unique identifier instead of username.

    Attributes:
        user_type (str): The type of user.
        username: None. The username field is removed.
        name (str): The user's full name.
        email (str): The user's email address.
        objects (MyUserManager): The manager class that handles user creation and querying.
        USERNAME_FIELD (str): The field to use for authentication. In this case, it's set to 'email'.
        REQUIRED_FIELDS (list): A list of fields required for user creation. In this case, it's set to 'name'.
    """
    user_type = models.CharField(max_length=20)
    username = None
    name = models.CharField(max_length=50, null=False)
    email = models.EmailField(unique=True, null=False)
    objects = MyUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']


class Product(models.Model):
    """
    A model representing a product in the store.

    Attributes:
        product_admin (MyUser): The admin user who added this product.
        category (str): The category of the product.
        name (str): The name of the product.
        brand (str): The brand of the product.
        size (str): The size of the product.
        price (Decimal): The price of the product.
        image (ImageField): The image of the product.
        date (date): The date when the product was added.

    Methods:
        order_quantity(): Calculate the total quantity of this product that has been ordered
            by summing up the quantity of all order items associated with this product.

    """
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


class UserProfile(models.Model):
    """
    A model representing a user's profile.

    Attributes:
        user (MyUser): The user whose profile this is.
        dob (datetime.date): The user's date of birth.
        address (str): The user's street address.
        city (str): The user's city.
        state (str): The user's state or province.
        country (str): The user's country.
        contact (phonenumbers.PhoneNumber): The user's phone number.
        pin (int): The user's postal code or ZIP code.
        image (str): The path to the user's profile image.
    """
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE, related_name='profile')
    dob = models.DateField(null=True)
    address = models.CharField(max_length=150, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    state = models.CharField(max_length=50, null=True, blank=True)
    country = models.CharField(max_length=50, null=True, blank=True)
    contact = PhoneNumberField(unique=True, null=True, blank=True)
    pin = models.PositiveIntegerField(null=True, blank=True)
    image = models.ImageField(upload_to='profile_images/', default='profile.png', null=True, blank=True)


class Coupon(models.Model):
    """
    A coupon model that can be applied to a cart to get a discount.

    Attributes:
        code (str): The unique code of the coupon.
        amount (int): The amount of discount to be applied.
        percentage (int): The percentage of discount to be applied.
    """
    code = models.CharField(max_length=50, unique=True)
    amount = models.IntegerField(null=True, blank=True)
    percentage = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    def __str__(self):
        return self.code


class UsedCoupon(models.Model):
    """
    A model that tracks used coupons for each user.

    Attributes:
        user (MyUser): The user who used the coupon.
        coupon (Coupon): The coupon that was used.
        active (bool): Whether the coupon is still active or not.
    """
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)


class Cart(models.Model):
    """
    A model that represents a user's shopping cart.

    Attributes:
        user (MyUser): The user who owns the cart.
        created (datetime): The datetime when the cart was created.
        updated (datetime): The datetime when the cart was last updated.
        total_price (Decimal): The total price of all items in the cart.
        user_coupon (UsedCoupon): The coupon used by the user, if any.
        discount (Decimal): The total discount applied to the cart.
        final_price (Decimal): The final price of the cart after applying the discount.
        checked_out (bool): Whether the cart has been checked out or not.

    Methods:
        update_total_price(): Update the total cart price based on the sum of all the cart items' 
            final prices.
        apply_coupon(): Applies the coupon discount to the cart total price based on the coupon 
            type (amount or percentage). Updates the cart discount and final price accordingly.
        save(): Overrides the default save method to update the final price of the cart based on 
            the discount applied.
    """
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    user_coupon = models.ForeignKey(UsedCoupon, on_delete=models.SET_NULL, null=True, blank=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    final_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    checked_out = models.BooleanField(default=False)

    def update_total_price(self):
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


class CartItem(models.Model):
    """
    A model that represents an item added to a cart.

    Attributes:
        cart (Cart): The cart that the item belongs to.
        product (Product): The product that the item represents.
        quantity (int): The quantity of the product.
        final_item_price (Decimal): The final price of the item after any discounts have been applied.
        created (DateTimeField): The date and time that the item was created.
        updated (DateTimeField): The date and time that the item was last updated.
    """
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    final_item_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class Order(models.Model):
    """
    A model that represents an order that has been placed.

    Attributes:
        cart (Cart): The cart that the order was created from.
        user (MyUser): The user who placed the order.
        billing_address (str): The billing address for the order.
        contact (PhoneNumberField): The contact phone number for the order.
        items (ManyToManyField): The products that are part of the order, through OrderItem.
        total_price (Decimal): The total price of the order before any discounts have been applied.
        coupon (Coupon): The coupon that was applied to the order, if any.
        discount (Decimal): The amount of the discount applied to the order.
        final_price (Decimal): The final price of the order after any discounts have been applied.
        created (DateTimeField): The date and time that the order was created.
        updated (DateTimeField): The date and time that the order was last updated.
        status (bool): The status of the order.
        is_paid (bool): Whether the order has been paid for.
    """
    cart = models.ForeignKey(Cart, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    billing_address = models.CharField(max_length=150, null=True, blank=True)
    contact = PhoneNumberField(null=True, blank=True)
    items = models.ManyToManyField(Product, through='OrderItem', related_name='orders')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    discount = models.DecimalField(default=0.00, decimal_places=2, max_digits=10)
    final_price = models.DecimalField(default=0.00, decimal_places=2, max_digits=10)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)
    is_paid = models.BooleanField(default=False)
    
    def __str__(self):
        return self.user.email


class OrderItem(models.Model):
    """
    A model that represents an item in an order.

    Attributes:
        order (Order): The order that the item belongs to.
        product (Product): The product that the item represents.
        quantity (int): The quantity of the product.
        final_item_price (Decimal): The final price of the item after any discounts have been applied.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    final_item_price = models.DecimalField(max_digits=10, decimal_places=2, null=False)