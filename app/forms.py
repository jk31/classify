from django import forms
from django.core.validators import FileExtensionValidator

class UploadFileForm(forms.Form):
    data = forms.FileField(validators=[FileExtensionValidator(allowed_extensions=["xlsx"])])


# class SelectVariablesForm(forms.Form):
#     variables = forms.MultipleChoiceField(
#         widget  = forms.CheckboxSelectMultiple(),
#     )