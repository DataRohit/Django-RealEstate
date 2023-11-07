# Djagno imports
from django import forms


# Custom modified ChoiceField
class CustomChoiceField(forms.ChoiceField):
    # Add a hidden field for the id
    id = forms.CharField(widget=forms.HiddenInput())

    # Constructor
    def __init__(self, *args, **kwargs):
        # Pop the description
        self.description = kwargs.pop("description", "")

        # Call the super constructor
        super(CustomChoiceField, self).__init__(*args, **kwargs)
