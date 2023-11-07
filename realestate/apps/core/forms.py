from django import forms


class CustomChoiceField(forms.ChoiceField):
    id = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        self.description = kwargs.pop("description", "")
        super(CustomChoiceField, self).__init__(*args, **kwargs)
