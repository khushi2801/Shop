from django.contrib import admin
from clothstore.models import myUser, Product

# Register your models here.
# admin.site.register(myUser)
# admin.site.register(Product)

@admin.register(myUser)
class myUserAdmin(admin.ModelAdmin):
    list_display = ("name", "user_type")
    # pass

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("product_admin", "category", "name")

    # def show_product_admin_name(self, obj):
    #     # name = obj.product_admin.name
    #     name = Product.objects.filter(myUser=obj)
    #     return name

    # show_product_admin_name.short_description = "Students"

    # pass

# @admin.register(Grade)
# class GradeAdmin(admin.ModelAdmin):
#     pass