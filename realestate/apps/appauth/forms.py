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
    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(
            attrs={"autocomplete": "current-password", "placeholder": "Password"}
        ),
    )

    class Meta:
        model = User
        fields = ("username", "password")


class RegisterForm(UserCreationForm):
    username = forms.EmailField(
        label="Email Address",
        widget=forms.TextInput(
            attrs={"autofocus": True, "placeholder": "Email Address", "type": "email"}
        ),
    )
    first_name = forms.CharField(
        label="First Name",
        widget=forms.TextInput(attrs={"placeholder": "First Name"}),
    )
    last_name = forms.CharField(
        label="Last Name",
        widget=forms.TextInput(attrs={"placeholder": "Last Name"}),
    )
    phone = forms.CharField(
        label="Phone Number",
        widget=forms.TextInput(attrs={"placeholder": "Phone Number"}),
    )
    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(
            attrs={"autocomplete": "new-password", "placeholder": "Password"}
        ),
    )
    password2 = forms.CharField(
        label="Password confirmation",
        strip=False,
        widget=forms.PasswordInput(
            attrs={"autocomplete": "new-password", "placeholder": "Confirm Password"}
        ),
    )

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "phone",
            "password1",
            "password2",
        )

    def save(self, commit=True):
        user = super(RegisterForm, self).save(commit=False)
        user.username = self.cleaned_data["username"]
        user.email = self.cleaned_data["username"]
        user.phone = self.cleaned_data["phone"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user
