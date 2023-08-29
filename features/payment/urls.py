from django.urls import path

from features.payment.views import checkout_fail, checkout_success, checkout_cart


app_name = 'payment'
urlpatterns = [
    path('checkout_cart/', checkout_cart, name='checkout_cart'),
    path('fail/', checkout_fail, name='checkout_fail'),
    path('success/', checkout_success, name='checkout_success'),
]