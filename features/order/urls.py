from django.urls import path
from features.order.views import my_order, order_operations, generate_pdf, order_operations


app_name = 'order'
urlpatterns = [
    path('my_order/', my_order, name='my_order'),
    path('order_summary/<int:order_id>/', order_operations, name='order_summary'),
    path('cancel_order/<int:order_id>/', order_operations, name='cancel_order'),
    path('generate_pdf/<int:order_id>/', generate_pdf, name='generate_pdf'),
]