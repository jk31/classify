from django.contrib import admin
from .models import ClassificationModel, Dataset, CustomUser
# Register your models here.

class DatasetAdmin(admin.ModelAdmin):
    readonly_fields = ("created", "pk")

admin.site.register(CustomUser)
admin.site.register(ClassificationModel)
admin.site.register(Dataset, DatasetAdmin)