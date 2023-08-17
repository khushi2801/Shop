import datetime
from features.account.models import MyUser
from django.db import models
from features.order.models import OrderItem


class Product(models.Model):
    """
    A model representing a product in the store.

    Attributes:
        seller (MyUser): The seller who added this product.
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
    seller = models.ForeignKey(MyUser, on_delete=models.CASCADE)
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