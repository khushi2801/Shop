import decimal
from features.account.models import MyUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from features.clothes.models import Product


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
    A model that tracks used coupons for each customer.

    Attributes:
        customer (MyUser): The customer who used the coupon.
        coupon (Coupon): The coupon that was used.
        active (bool): Whether the coupon is still active or not.
    """
    customer = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)


class Cart(models.Model):
    """
    A model that represents a customer's shopping cart.

    Attributes:
        customer (MyUser): The customer who owns the cart.
        created (datetime): The datetime when the cart was created.
        updated (datetime): The datetime when the cart was last updated.
        total_price (Decimal): The total price of all items in the cart.
        customer_coupon (UsedCoupon): The coupon used by the customer, if any.
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
    customer = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    customer_coupon = models.ForeignKey(UsedCoupon, on_delete=models.SET_NULL, null=True, blank=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    final_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    checked_out = models.BooleanField(default=False)

    def update_total_price(self):
        self.total_price = sum(item.final_item_price for item in self.cart_items.all())
        if not self.total_price:
            self.customer_coupon = None
            self.discount = 0
        self.save()

    def apply_coupon(self):
        if self.customer_coupon.coupon.amount:
            self.discount = self.customer_coupon.coupon.amount
        if self.customer_coupon.coupon.percentage:
            self.discount = self.total_price * self.customer_coupon.coupon.percentage / 100
        self.update_total_price()

    def save(self, *args, **kwargs):
        if self.pk is not None:
            self.final_price = self.total_price - decimal.Decimal(str(self.discount))
        super(Cart, self).save(*args, **kwargs)

    def __str__(self):
        return self.customer.email


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