from django.urls import path
from features.store.views import add_to_cart, buy_now, dashboard


app_name = 'store'
urlpatterns = [
    # URLs for Customers
    path('add_to_cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('buy_now/<int:product_id>', buy_now, name='buy_now'),

    # URLs for Merchants
    path('dashboard/', dashboard, name='dashboard'),
]