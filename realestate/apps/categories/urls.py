from django.urls import path
from .views import (
    CategoryListView,
    CategoryAddView,
    CategoryEditView,
    CategoryDeleteView,
)


urlpatterns = [
    path("", CategoryListView.as_view(), name="category-list"),
    path("add/", CategoryAddView.as_view(), name="category-add"),
    path("edit/<str:category_id>/", CategoryEditView.as_view(), name="category-edit"),
    path(
        "delete/<str:category_id>/",
        CategoryDeleteView.as_view(),
        name="category-delete",
    ),
]
