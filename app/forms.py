from django import forms
from django.core.validators import FileExtensionValidator

class UploadFileForm(forms.Form):
    data = forms.FileField(validators=[FileExtensionValidator(allowed_extensions=['csv', "xlsx"])])