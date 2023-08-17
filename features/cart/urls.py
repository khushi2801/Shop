from django.urls import path
from features.cart.views import my_cart, apply_coupon, update_cart_items


app_name = 'cart'
urlpatterns = [
    path('my_cart/', my_cart, name='my_cart'),
    path('apply_coupon/<str:coupon_code>', apply_coupon, name='apply_coupon'),
    path('update_cart_items/<int:product_id>/<int:quantity>/', update_cart_items, name='update_cart_items'),
]