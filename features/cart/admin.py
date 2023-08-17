from django.contrib import admin
from .models import Cart, CartItem, Coupon, UsedCoupon


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("customer", "total_price")

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("cart", "product", "quantity")

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ("code", "amount", "percentage")

@admin.register(UsedCoupon)
class UsedCouponAdmin(admin.ModelAdmin):
    list_display = ("customer", "coupon", "active")