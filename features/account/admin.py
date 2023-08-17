from django.contrib import admin
from .models import MyUser, UserProfile


@admin.register(MyUser)
class MyUserAdmin(admin.ModelAdmin):
    list_display = ("email", "name", "user_type")

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "contact")