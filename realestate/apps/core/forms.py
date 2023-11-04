from django import forms

from realestate.apps.core.models import Category


class CustomChoiceField(forms.ChoiceField):
    def __init__(self, *args, **kwargs):
        self.description = kwargs.pop("description", "")
        super(CustomChoiceField, self).__init__(*args, **kwargs)


class EvalHouseForm(forms.Form):
    def __init__(self, *args, **kwargs):
        extra_fields = kwargs.pop("extra_fields", None)
        categories = kwargs.pop("categories", None)
        super(EvalHouseForm, self).__init__(*args, **kwargs)

        if extra_fields:
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
                    widget=forms.Select(attrs={"class": "custom-form-select"}),
                )
                self.fields[field_name] = field


class AddCategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ("summary", "description")


class EditCategoryForm(forms.ModelForm):
    category_id = forms.IntegerField(widget=forms.HiddenInput())

    class Meta:
        model = Category
        fields = ("summary", "description")
