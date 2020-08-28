from django import forms
from django.forms import BaseFormSet

from app.models import Dataset


class DatasetUploadForm(forms.ModelForm):
    class Meta:
        model = Dataset
        fields = ("dataset",)


class TrainingForm(forms.Form):
    def __init__(self, columns, *args, **kwargs):
        super().__init__(*args, **kwargs)

        choices = tuple([(col, col) for col in columns if columns[col] == "Choice"])
        field = forms.ChoiceField(choices=choices)
        self.fields["goal"] = field
        
        for col in columns:
            field = forms.BooleanField(widget=forms.CheckboxInput, required=False)
            self.fields[f"checkbox_{col}"] = field


class SaveModelForm(forms.Form):
    model_pk = forms.IntegerField(widget = forms.HiddenInput(), required=True)

        
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