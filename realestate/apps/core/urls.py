# Django imports
from django.urls import path


# Import views for the app
from .views import HomeView
from .views import ReportView


# Set the url patters for the app
urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("report/<str:couple_id>/", ReportView.as_view(), name="report"),
]
