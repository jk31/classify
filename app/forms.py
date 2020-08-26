from django import forms
from django.forms import BaseFormSet
from django.core.validators import FileExtensionValidator

class UploadFileForm(forms.Form):
    data = forms.FileField(validators=[FileExtensionValidator(allowed_extensions=["xlsx"])])


class PredictForm(forms.Form):
    def __init__(self, variables, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for var in variables:
            if variables[var] == "Numerical":
                field = forms.FloatField(required=True)
                self.fields[f"field_{var}"] = field
            elif type(variables[var] == list):
                choices = tuple([(x, x) for x in variables[var]])
                field = forms.ChoiceField(choices=choices)
                self.fields[f"field_{var}"] = field