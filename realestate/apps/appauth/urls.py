# Django imports
from django.urls import path


# Import views for the urls
from .views import LoginView
from .views import LogoutView
from .views import HomebuyerSignupView
from .views import RealtorSignupView
from .views import PasswordChangeView


# Add the url patters for the app
urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path(
        "homebuyer-signup/<str:registration_token>",
        HomebuyerSignupView.as_view(),
        name="homebuyer-signup",
    ),
    path("realtor-signup/", RealtorSignupView.as_view(), name="realtor-signup"),
    path("password-change/", PasswordChangeView.as_view(), name="password-change"),
]
