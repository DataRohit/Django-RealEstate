# Imports
from django.urls import path, include
from realestate.apps.appauth import views as appauth_views

# Urls
urlpatterns = [
    path("login/", view=appauth_views.LoginView.as_view(), name="appauth_login"),
    path("logout/", view=appauth_views.LogoutView.as_view(), name="appauth_logout"),
]
