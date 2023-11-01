# Imports
from django import forms
from realestate.apps.appauth.models import User
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm


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
