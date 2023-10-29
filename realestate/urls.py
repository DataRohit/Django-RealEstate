# Imports
from django.contrib import admin
from django.urls import path, include


# Base urls for the app
urlpatterns = [
    path("admin/", admin.site.urls, name="admin"),
    path("", include("realestate.apps.core.urls"), name="core"),
    path("appauth/", include("realestate.apps.appauth.urls"), name="appauth"),
]
