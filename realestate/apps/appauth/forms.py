from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

from realestate.apps.appauth.models import User


class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email Address",
        widget=forms.TextInput(
            attrs={"autofocus": True, "placeholder": "Email Address", "type": "email"}
        ),
    )

    class Meta:
        model = User
        fields = ("username",)


class RealtorSignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            "email",
            "first_name",
            "last_name",
            "phone",
            "password1",
            "password2",
        )


class HomebuyerSignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "phone",
            "password1",
            "password2",
        )


class PasswordChangeForm(PasswordChangeForm):
    class Meta:
        model = User
        fields = [
            "old_password",
            "new_password1",
            "new_password2",
        ]
        widgets = {"password": forms.PasswordInput}
