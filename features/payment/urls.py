from django.urls import path
from features.payment.views import checkout


app_name = 'payment'
urlpatterns = [
    path('checkout/', checkout, name='checkout'), 
]