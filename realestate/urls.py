# Imports
from django.contrib import admin
from django.urls import path


# Base urls for the app
urlpatterns = [
    path("admin/", admin.site.urls),
]
