from django.contrib import admin
from django.urls import path, include


# Base urls for the app
urlpatterns = [
    path("admin/", admin.site.urls, name="admin"),
    path("", include("realestate.apps.appauth.urls")),
    path("", include("realestate.apps.core.urls")),
    path("", include("realestate.apps.pending.urls")),
    path("house/", include("realestate.apps.house.urls")),
    path("categories/", include("realestate.apps.categories.urls")),
]
