from django import forms


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
                    choices=((1, "1"), (2, "2"), (3, "3"), (4, "4"), (5, "5")),
                    label=category.summary,
                    description=category.description,
                    widget=forms.Select(attrs={"class": "custom-form-select"}),
                )
                self.fields[field_name] = field
