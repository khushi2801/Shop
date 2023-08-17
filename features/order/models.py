from features.account.models import MyUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class Order(models.Model):
    """
    A model that represents an order that has been placed.

    Attributes:
        cart (Cart): The cart that the order was created from.
        customer (MyUser): The customer who placed the order.
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
    cart = models.ForeignKey("cart.Cart", on_delete=models.SET_NULL, null=True, blank=True)
    customer = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    billing_address = models.CharField(max_length=150, null=True, blank=True)
    contact = PhoneNumberField(null=True, blank=True)
    items = models.ManyToManyField("clothes.Product", through='OrderItem', related_name='orders')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    coupon = models.ForeignKey("cart.Coupon", on_delete=models.SET_NULL, null=True, blank=True)
    discount = models.DecimalField(default=0.00, decimal_places=2, max_digits=10)
    final_price = models.DecimalField(default=0.00, decimal_places=2, max_digits=10)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)
    is_paid = models.BooleanField(default=False)
    
    def __str__(self):
        return self.customer.email


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
    product = models.ForeignKey("clothes.Product", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    final_item_price = models.DecimalField(max_digits=10, decimal_places=2, null=False)