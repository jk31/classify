from django.contrib import admin
from .models import ClassificationModel, Dataset
# Register your models here.

admin.site.register(ClassificationModel)
admin.site.register(Dataset)