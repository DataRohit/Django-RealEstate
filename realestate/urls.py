# Imports
from django.contrib import admin
from django.urls import path

from realestate.apps.core import views as CoreViews
from realestate.apps.appauth import views as AppAuthViews
from realestate.apps.pending import views as PendingViews


# Base urls for the app
urlpatterns = [
    path("admin/", admin.site.urls, name="admin"),
    path("", CoreViews.HomeView.as_view(), name="home"),
    path(
        "house/edit/<str:house_id>",
        CoreViews.HouseEditView.as_view(),
        name="house-edit",
    ),
    path(
        "house/delete/<str:house_id>",
        CoreViews.HouseDeleteView.as_view(),
        name="house-delete",
    ),
    path(
        "house/add/",
        CoreViews.HouseAddView.as_view(),
        name="house-add",
    ),
    path("login/", AppAuthViews.LoginView.as_view(), name="login"),
    path("logout/", AppAuthViews.LogoutView.as_view(), name="logout"),
    path(
        "password_change/",
        AppAuthViews.PasswordChangeView.as_view(),
        {"post_change_redirect": "home"},
        name="password_change",
    ),
    path("invite/", PendingViews.InviteHomebuyerView.as_view(), name="invite"),
    path(
        "homebuyer-signup/<str:registration_token>/",
        AppAuthViews.SignupView.as_view(),
        name="homebuyer-signup",
    ),
    path(
        "realtor-signup/",
        AppAuthViews.RealtorSignupView.as_view(),
        name="realtor-signup",
    ),
    path("eval/<str:house_id>/", CoreViews.EvalView.as_view(), name="eval"),
    path("report/<str:house_id>/", CoreViews.ReportView.as_view(), name="report"),
    path("categories/", CoreViews.CategoryView.as_view(), name="categories"),
    path("categories/add/", CoreViews.CategoryAddView.as_view(), name="categories-add"),
    path(
        "categories/update/<str:category_id>",
        CoreViews.CategoryUpdateView.as_view(),
        name="categories-update",
    ),
    path(
        "categories/delete/<str:category_id>",
        CoreViews.CategoryDeleteView.as_view(),
        name="categories-delete",
    ),
]
