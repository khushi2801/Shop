from django.contrib import admin
from clothstore.models import MyUser, Product, UserProfile, Cart, Order, OrderItem

@admin.register(MyUser)
class MyUserAdmin(admin.ModelAdmin):
    list_display = ("email", "name", "user_type")

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("product_admin", "category", "name")

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "contact")

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "quantity")

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("user", "created", "updated")

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "quantity")