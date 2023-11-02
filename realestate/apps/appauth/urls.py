from django.urls import path
from realestate.apps.appauth import views

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path("auth/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("get-user/", views.APIUserInfoView.as_view(), name="api_get_user"),
    path("houses/", views.APIHouseView.as_view(), name="api_houses"),
]
