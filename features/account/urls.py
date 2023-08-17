from django.urls import path
from features.account.views import signup, login, logout, profile, update_profile


app_name = 'account'
urlpatterns = [
    # URLs common for all user types
    path('signup/', signup, name='signup'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('profile/', profile, name='profile'),
    path('update_profile/', update_profile, name='update_profile'),
]