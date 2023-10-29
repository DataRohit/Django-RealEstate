# Imports
from django.urls import include, path
from realestate.apps.core import views


urlpatterns = [
    path("", views.HomeView.as_view(), name="core_home"),
]
