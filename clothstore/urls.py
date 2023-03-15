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
    path('update_profile/<int:user_id>', views.update_profile_view, name='update_profile'),

    # Product Admin side
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('add_product/', views.add_product_view, name='add_product'),
    path('view_products/', views.view_products_view, name='view_products'),
    path('product_detail/<int:product_id>', views.product_detail_view, name='product_detail'),
    path('update_product/<int:product_id>', views.update_product_view, name='update_product'),
    path('delete_product/<int:product_id>', views.delete_product_view, name='delete_product'),

    # Customer side
    path('home/', views.home_view, name='home'),
]