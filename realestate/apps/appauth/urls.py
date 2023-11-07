from django.urls import path
from .views import (
    LoginView,
    LogoutView,
    HomebuyerSignupView,
    RealtorSignupView,
    PasswordChangeView,
)


urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("homebuyer-signup/", HomebuyerSignupView.as_view(), name="homebuyer-signup"),
    path("realtor-signup/", RealtorSignupView.as_view(), name="realtor-signup"),
    path("password-change/", PasswordChangeView.as_view(), name="password-change"),
]
