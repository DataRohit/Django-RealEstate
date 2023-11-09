# Django imports
from django import forms
from django.core.exceptions import ValidationError


# App imports
from realestate.apps.appauth.models import User
from realestate.apps.pending.models import PendingHomebuyer


# Form to invite homebuyers
class InviteHomebuyerForm(forms.Form):
    # Set the fields for the form
    email = forms.EmailField(
        label="Email",
        widget=forms.TextInput(
            attrs={
                "autofocus": True,
                "placeholder": "Email",
                "type": "email",
                "class": "form-control",
            }
        ),
    )
    first_name = forms.CharField(
        label="First Name",
        max_length=30,
        widget=forms.TextInput(
            attrs={"placeholder": "First Name", "class": "form-control mt-3"}
        ),
    )
    last_name = forms.CharField(
        label="Last Name",
        max_length=30,
        widget=forms.TextInput(
            attrs={"placeholder": "Last Name", "class": "form-control mt-3"}
        ),
    )

    # Method to check if the email is unique
    def _confirm_unique(self, cleaned_data, email_fieldname):
        # Get the email
        email = cleaned_data.get(email_fieldname)

        # Check if the email already exists
        if email:
            for model in (User, PendingHomebuyer):
                if model.objects.filter(email=email).exists():
                    self.add_error(
                        email_fieldname,
                        ValidationError(
                            "A user with this email already exists or has been invited."
                        ),
                    )

        # If the email is unique, return it
        return email

    # Method to clean the form
    def clean(self):
        # Run the parent clean method and get the cleaned data
        cleaned_data = super(InviteHomebuyerForm, self).clean()

        # Check if email is unique
        self._confirm_unique(cleaned_data, "email")

        # Return the cleaned data
        return cleaned_data
