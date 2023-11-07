# Django imports
from django import forms


# App imports
from .models import Category
from realestate.apps.core.forms import CustomChoiceField


# Form to edit the category weights
class CategoryWeightEditForm(forms.Form):
    # Constructor
    def __init__(self, *args, **kwargs):
        # Get the extra fields
        extra_fields = kwargs.pop("extra_fields", None)

        # Get the categories
        categories = kwargs.pop("categories", None)

        # Call the parent constructor
        super(CategoryWeightEditForm, self).__init__(*args, **kwargs)

        # If the extra fields are not None
        if extra_fields:
            # Traverse the categories and extra fields
            for category, (field_name, field_value) in zip(
                categories, extra_fields.items()
            ):
                # Create a custom choice field
                field = CustomChoiceField(
                    initial=field_value,
                    choices=(
                        (1, "Unimportant"),
                        (2, "Below Average"),
                        (3, "Average"),
                        (4, "Above Average"),
                        (5, "Important"),
                    ),
                    label=category.summary,
                    description=category.description,
                    widget=forms.Select(),
                )

                # Set the field id
                field.id = category.id

                # Add the field to the form
                self.fields[field_name] = field


# Form to edit the category
class CategoryEditForm(forms.Form):
    # Add the fields to the form
    summary = forms.CharField(
        label="Summary",
        widget=forms.TextInput(attrs={"placeholder": "Summary"}),
    )
    description = forms.CharField(
        label="Description",
        widget=forms.Textarea(attrs={"placeholder": "Description", "rows": 5}),
    )

    # Meta class
    class Meta:
        # Set the model and fields for the form
        model = Category
        fields = ["summary", "description"]


# Form to delete the category
class CategoryDeleteForm(forms.Form):
    # Add the fields to the form with disabled inputs
    summary = forms.CharField(
        label="Summary",
        widget=forms.TextInput(attrs={"placeholder": "Summary", "disabled": True}),
    )
    description = forms.CharField(
        label="Description",
        widget=forms.Textarea(
            attrs={"placeholder": "Description", "rows": 5, "disabled": True}
        ),
    )

    # Meta class
    class Meta:
        # Set the model and fields for the form
        model = Category
        fields = ["summary", "description"]
