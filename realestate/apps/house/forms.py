# Django imports
from django import forms


# App imports
from .models import House
from realestate.apps.core.forms import CustomChoiceField


# Form for Creating/Editting a House
class HouseEditForm(forms.Form):
    # Fields for the form
    nickname = forms.CharField(
        label="Nickname",
        widget=forms.TextInput(attrs={"placeholder": "Nickname"}),
    )
    address = forms.CharField(
        label="Address",
        widget=forms.Textarea(attrs={"placeholder": "Address", "rows": 5}),
    )

    # Meta class
    class Meta:
        model = House
        fields = ["nickname", "address"]


# Form to delete a house
class HouseDeleteForm(forms.Form):
    # Fields for the form with disabled inputs
    nickname = forms.CharField(
        label="Nickname",
        widget=forms.TextInput(attrs={"placeholder": "Nickname", "disabled": True}),
    )
    address = forms.CharField(
        label="Address",
        widget=forms.Textarea(
            attrs={"placeholder": "Address", "rows": 5, "disabled": True}
        ),
    )

    # Meta class
    class Meta:
        model = House
        fields = ["nickname", "address"]


# Form to evaluate a house
class HouseEvalForm(forms.Form):
    # Constructor
    def __init__(self, *args, **kwargs):
        # Get the extra fields and categories
        extra_fields = kwargs.pop("extra_fields", None)
        categories = kwargs.pop("categories", None)

        # Call the parent constructor
        super(HouseEvalForm, self).__init__(*args, **kwargs)

        # If the extra fields exists
        if extra_fields:
            # Traverse over the categories and extra fields
            for category, (field_name, field_value) in zip(
                categories, extra_fields.items()
            ):
                field = CustomChoiceField(
                    initial=field_value,
                    choices=(
                        (1, "Poor"),
                        (2, "Below Average"),
                        (3, "Average"),
                        (4, "Above Average"),
                        (5, "Excellent"),
                    ),
                    label=category.summary,
                    description=category.description,
                    widget=forms.Select(),
                )

                # Add the field to the form
                self.fields[field_name] = field
