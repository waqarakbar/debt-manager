from django.urls import path
from .views import user_login, user_logout, user_register, profile, user_password_change

urlpatterns = [
    path("user-login/", user_login, name='user-login'),
    path("user-logout/", user_logout, name='user-logout'),
    path("user-register/", user_register, name='user-register'),
    path("profile/", profile, name='profile'),
    path("password/", user_password_change, name='password'),
]