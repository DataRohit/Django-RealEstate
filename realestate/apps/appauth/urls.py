# Imports
from django.urls import path, include
from realestate.apps.appauth import views

# Urls
urlpatterns = [
    path("login/", view=views.LoginView.as_view(), name="appauth_login"),
    path("logout/", view=views.LogoutView.as_view(), name="appauth_logout"),
]
