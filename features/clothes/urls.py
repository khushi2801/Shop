from django.urls import path
from features.clothes.views import product_detail, add_product, view_products, update_product, delete_product


app_name = 'clothes'
urlpatterns = [
    path('product_detail/<int:product_id>', product_detail, name='product_detail'),    
    path('add_product/', add_product, name='add_product'),
    path('view_products/', view_products, name='view_products'),
    path('update_product/<int:product_id>', update_product, name='update_product'),
    path('delete_product/<int:product_id>', delete_product, name='delete_product'),
]