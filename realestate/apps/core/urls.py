from django.urls import path
from .views import HomeView, ReportView


urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("report/<str:house_id>/", ReportView.as_view(), name="report"),
]
