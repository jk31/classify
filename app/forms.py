from crispy_forms.helper import FormHelper

from django import forms
from django.forms import BaseFormSet

from app.models import Dataset


class DatasetUploadForm(forms.ModelForm):
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     for visible in self.visible_fields():
    #         visible.field.widget.attrs["class"] = "btn btn-success"
            
    class Meta:
        model = Dataset
        fields = ("dataset",)


class TrainingForm(forms.Form):
    def __init__(self, columns, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""

        choices = tuple([(col, col) for col in columns])
        #  if columns[col] == "Choice"
        field = forms.ChoiceField(choices=choices)
        self.fields["goal"] = field
        self.fields["goal"].label = "What do you want to predict?"
        
        for col in columns:
            field = forms.BooleanField(widget=forms.CheckboxInput, required=False)
            self.fields[f"variable_{col}"] = field
            self.fields[f"variable_{col}"].label = col

        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'


class SaveModelForm(forms.Form):
    model_pk = forms.IntegerField(widget = forms.HiddenInput(), required=True)

        
class PredictForm(forms.Form):
    def __init__(self, variables, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for var in variables:
            if variables[var] == "Numerical":
                field = forms.FloatField(required=True)
                self.fields[var] = field
            elif type(variables[var] == list):
                choices = tuple([(x, x) for x in variables[var]])
                field = forms.ChoiceField(choices=choices)
                self.fields[var] = field
        
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'