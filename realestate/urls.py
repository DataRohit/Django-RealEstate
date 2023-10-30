# Imports
from django.contrib import admin
from django.urls import path

from realestate.apps.core import views as core_views
from realestate.apps.appauth import views as appauth_views


# Base urls for the app
urlpatterns = [
    path("admin/", admin.site.urls, name="admin"),
    path("", core_views.HomeView.as_view(), name="home"),
    path("login/", appauth_views.LoginView.as_view(), name="login"),
    path("logout/", appauth_views.LogoutView.as_view(), name="logout"),
]
