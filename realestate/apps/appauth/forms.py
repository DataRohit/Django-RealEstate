# Imports
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError

from realestate.apps.appauth.models import User


# Form class
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


class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "phone",
            "password1",
            "password2",
        ]
        widgets = {"password": forms.PasswordInput}

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(SignupForm, self).clean()
        password = cleaned_data.get("password1")
        password_confirmation = cleaned_data.get("password2")
        if password and password_confirmation and password != password_confirmation:
            self.add_error(
                "password_confirmation", ValidationError("Passwords do not match.")
            )
        return cleaned_data
