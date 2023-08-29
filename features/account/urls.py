from django.urls import path
from features.account.views import user_signup, user_login, user_logout, user_profile, update_profile


app_name = 'account'
urlpatterns = [
    # URLs common for all user types
    path('signup/', user_signup, name='signup'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('profile/', user_profile, name='profile'),
    path('update_profile/', update_profile, name='update_profile'),
]