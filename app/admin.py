from django.contrib import admin
from .models import ClassificationModel, Dataset
# Register your models here.

class DatasetAdmin(admin.ModelAdmin):
    readonly_fields = ("created", )

admin.site.register(ClassificationModel)
admin.site.register(Dataset, DatasetAdmin)