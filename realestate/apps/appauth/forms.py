# Django imports
from django import forms
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.forms import UserCreationForm


# App imports
from realestate.apps.appauth.models import User


# Class for Login Form
class LoginForm(AuthenticationForm):
    # Field for username
    username = forms.EmailField(
        label="Email Address",
        widget=forms.TextInput(
            attrs={"autofocus": True, "placeholder": "Email Address", "type": "email"}
        ),
    )

    # Meta class for form
    class Meta:
        # Set the model and fields for the form
        model = User
        fields = ("username",)


# Class for Realtor Signup Form
class RealtorSignupForm(UserCreationForm):
    # Meta class for form
    class Meta:
        # Set the model and fields for the form
        model = User
        fields = (
            "email",
            "first_name",
            "last_name",
            "phone",
            "password1",
            "password2",
        )


# Class for Homebuyer Signup Form
class HomebuyerSignupForm(UserCreationForm):
    # Meta class for form
    class Meta:
        # Set the model and fields for the form
        model = User
        fields = (
            "first_name",
            "last_name",
            "phone",
            "password1",
            "password2",
        )


# Class for Password Change Form
class PasswordChangeForm(PasswordChangeForm):
    # Meta class for form
    class Meta:
        # Set the model and fields for the form
        model = User
        fields = [
            "old_password",
            "new_password1",
            "new_password2",
        ]

        # Set the widget for the password field
        widgets = {"password": forms.PasswordInput}
