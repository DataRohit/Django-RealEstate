import re

from django import forms
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


class SignupForm(forms.ModelForm):
    registration_token = forms.CharField(
        min_length=64, max_length=64, widget=forms.widgets.HiddenInput
    )
    phone = forms.CharField(max_length=20)

    class Meta:
        model = User
        fields = ("registration_token", "email", "first_name", "last_name", "phone")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email and User.objects.filter(email=email).exists():
            error = ValidationError("User with this email already exists.")
            self.add_error("email", error)
        return email

    def clean_registration_token(self):
        token = self.cleaned_data.get("registration_token")
        homebuyer = PendingHomebuyer.objects.filter(registration_token=token)
        if not homebuyer.exists():
            self.add_error(
                "registration_token", ValidationError("Invalid Registration Token.")
            )
        return homebuyer.first()

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if not re.match(r"^\+?\d{9,15}$", phone):
            raise ValidationError("Invalid phone number.")
        return phone
