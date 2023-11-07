# Django imports
from django import forms
from django.core.exceptions import ValidationError


# App imports
from realestate.apps.appauth.models import User
from realestate.apps.pending.models import PendingHomebuyer


# Form to invite homebuyers
class InviteHomebuyerForm(forms.Form):
    # Set the fields for the form
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

        # Get the cleaned emails
        first_email = self._confirm_unique(cleaned_data, "first_email")
        second_email = self._confirm_unique(cleaned_data, "second_email")

        # If the emails are the same
        if first_email and second_email and first_email == second_email:
            # Raise the validation error
            self.add_error(None, ValidationError("Emails must be distinct."))

        # Return the cleaned data
        return cleaned_data
