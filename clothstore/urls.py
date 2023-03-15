from django.contrib import admin
from django.urls import path
from clothstore import views

app_name = 'clothstore'
urlpatterns = [
    path('admin/', admin.site.urls),
    # path('index/', views.index_view, name='index'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('home/', views.home_view, name='home'),
    # path('home/<str:customer_name>', views.home_view, name='home'),
    path('logout/', views.logout_view, name='logout'),
    # path("success/", views.success, name="success"),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    # path('dashboard/<str:product_admin_name>', views.dashboard_view, name='dashboard'),
    path('add_product/', views.add_product_view, name='add_product'),
    path('view_products/', views.view_products_view, name='view_products'),
    path('product_detail/<int:product_id>', views.product_detail_view, name='product_detail'),
    path('update_product/<int:product_id>', views.update_product_view, name='update_product'),
    path('delete_product/<int:product_id>', views.delete_product_view, name='delete_product'),
]