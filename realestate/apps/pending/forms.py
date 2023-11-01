from django import forms
from django.contrib.auth import forms as AuthForms
from django.core.exceptions import ValidationError

from realestate.apps.appauth.models import User
from realestate.apps.pending.models import PendingHomebuyer


class InviteHomebuyerForm(forms.Form):
    first_email = forms.EmailField(
        label="Email",
        widget=forms.TextInput(
            attrs={"autofocus": True, "placeholder": "Buyer 1", "type": "email"}
        ),
    )
    second_email = forms.EmailField(
        label="Email",
        widget=forms.TextInput(
            attrs={"autofocus": True, "placeholder": "Buyer 2", "type": "email"}
        ),
    )

    def _confirm_unique(self, cleaned_data, email_fieldname):
        email = cleaned_data.get(email_fieldname)
        if email:
            for model in (User, PendingHomebuyer):
                if model.objects.filter(email=email).exists():
                    self.add_error(
                        email_fieldname,
                        ValidationError(
                            "A user with this email already exists or has been invited."
                        ),
                    )
        return email

    def clean(self):
        cleaned_data = super(InviteHomebuyerForm, self).clean()

        first_email = self._confirm_unique(cleaned_data, "first_email")
        second_email = self._confirm_unique(cleaned_data, "second_email")

        if first_email and second_email and first_email == second_email:
            self.add_error(None, ValidationError("Emails must be distinct."))
        return cleaned_data


class SignupForm(AuthForms.UserCreationForm):
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
