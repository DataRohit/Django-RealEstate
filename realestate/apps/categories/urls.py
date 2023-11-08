# Django imports
from django.urls import path


# Import views for the urls
from .views import CategoryAddView
from .views import CategoryDeleteView
from .views import CategoryEditView
from .views import CategoryListView


# Add the url patters for the app
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
