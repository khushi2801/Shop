from django.contrib import admin
from django.urls import path
from clothstore import views

app_name = 'clothstore'
urlpatterns = [
    path('admin/', admin.site.urls),

    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('update_profile/', views.update_profile_view, name='update_profile'),

    # Product Admin side
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('add_product/', views.add_product_view, name='add_product'),
    path('view_products/', views.view_products_view, name='view_products'),
    path('product_detail/<int:product_id>', views.product_detail_view, name='product_detail'),
    path('update_product/<int:product_id>', views.update_product_view, name='update_product'),
    path('delete_product/<int:product_id>', views.delete_product_view, name='delete_product'),

    # Customer side
    path('home/', views.home_view, name='home'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('buy_now/<int:product_id>', views.buy_now, name='buy_now'),
    path('my_order/', views.my_order_view, name='my_order'),
    path('order_summary/<int:order_id>/', views.order_operations, name='order_summary'),
    path('generate_pdf/<int:order_id>/', views.generate_pdf, name='generate_pdf'),
    path('cancel_order/<int:order_id>/', views.order_operations, name='cancel_order'),
    path('cart/', views.cart_view, name='cart'),
    path('update_cart_items/<int:product_id>/<int:quantity>/', views.update_cart_items, name='update_cart_items'),
    path('checkout/', views.checkout, name='checkout'),
    
]