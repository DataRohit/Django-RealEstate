# Imports
from django.urls import path, include
from django.contrib.auth import views as auth_views

# Urls
urlpatterns = [
    path("login/", view=auth_views.LoginView.as_view(), name="appauth_login"),
    path("logout/", view=auth_views.LogoutView.as_view(), name="appauth_logout"),
]
