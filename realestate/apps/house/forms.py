from django import forms
from .models import House
from realestate.apps.core.forms import CustomChoiceField


class HouseEditForm(forms.Form):
    nickname = forms.CharField(
        label="Nickname",
        widget=forms.TextInput(attrs={"placeholder": "Nickname"}),
    )
    address = forms.CharField(
        label="Address",
        widget=forms.Textarea(attrs={"placeholder": "Address", "rows": 5}),
    )

    class Meta:
        model = House
        fields = ["nickname", "address"]


class HouseDeleteForm(forms.Form):
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

    class Meta:
        model = House
        fields = ["nickname", "address"]


class HouseEvalForm(forms.Form):
    def __init__(self, *args, **kwargs):
        extra_fields = kwargs.pop("extra_fields", None)
        categories = kwargs.pop("categories", None)
        super(HouseEvalForm, self).__init__(*args, **kwargs)

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
                    widget=forms.Select(),
                )
                self.fields[field_name] = field
