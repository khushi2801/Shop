from django.contrib import admin
from clothstore.models import MyUser, Product, UserProfile

@admin.register(MyUser)
class MyUserAdmin(admin.ModelAdmin):
    list_display = ("name", "user_type")

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("product_admin", "category", "name")

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "contact")