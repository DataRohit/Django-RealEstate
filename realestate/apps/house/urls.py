from django.urls import path
from .views import HouseAddView, HouseEditView, HouseDeleteView, HouseEvalView


urlpatterns = [
    path("add/", HouseAddView.as_view(), name="house-add"),
    path("edit/<str:house_id>/", HouseEditView.as_view(), name="house-edit"),
    path("delete/<str:house_id>/", HouseDeleteView.as_view(), name="house-delete"),
    path("eval/<str:house_id>/", HouseEvalView.as_view(), name="house-eval"),
]
