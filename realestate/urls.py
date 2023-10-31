# Imports
from django.contrib import admin
from django.urls import path, include

from realestate.apps.core import views as CoreViews
from realestate.apps.appauth import views as AppAuthViews
from realestate.apps.pending import views as PendingViews


# Base urls for the app
urlpatterns = [
    path("admin/", admin.site.urls, name="admin"),
    path("", CoreViews.HomeView.as_view(), name="home"),
    path("api/", include("realestate.apps.appauth.urls")),
    path("login/", AppAuthViews.LoginView.as_view(), name="login"),
    path("logout/", AppAuthViews.LogoutView.as_view(), name="logout"),
    path("invite/", PendingViews.InviteHomebuyerView.as_view(), name="invite"),
]
