from django import forms
from .models import Category
from realestate.apps.core.forms import CustomChoiceField


class CategoryWeightEditForm(forms.Form):
    def __init__(self, *args, **kwargs):
        extra_fields = kwargs.pop("extra_fields", None)
        categories = kwargs.pop("categories", None)
        super(CategoryWeightEditForm, self).__init__(*args, **kwargs)

        if extra_fields:
            for category, (field_name, field_value) in zip(
                categories, extra_fields.items()
            ):
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
                field.id = category.id
                self.fields[field_name] = field


class CategoryEditForm(forms.Form):
    summary = forms.CharField(
        label="Summary",
        widget=forms.TextInput(attrs={"placeholder": "Summary"}),
    )
    description = forms.CharField(
        label="Description",
        widget=forms.Textarea(attrs={"placeholder": "Description", "rows": 5}),
    )

    class Meta:
        model = Category
        fields = ["summary", "description"]


class CategoryDeleteForm(forms.Form):
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

    class Meta:
        model = Category
        fields = ["summary", "description"]
