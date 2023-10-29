# Imports
from django.contrib import admin
from django.urls import path, include


# Base urls for the app
urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("realestate.apps.core.urls")),
]
