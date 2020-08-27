from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator

import uuid
from annoying.fields import JSONField

# Create your models here.


class Dataset(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="owner_datasets", on_delete=models.CASCADE, blank=True, null=True)
    dataset = models.FileField(upload_to="datasets/", validators=[FileExtensionValidator(allowed_extensions=["xlsx"])])

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created",)

    def __str__(self):
        return self.name


class ClassificationModel(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="owner_models", on_delete=models.CASCADE, blank=True, null=True)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='models')

    created = models.DateTimeField(auto_now_add=True)

    training_columns = JSONField(blank=True, null=True)
    variables = JSONField(blank=True, null=True)
    goal = models.CharField(max_length=100, blank=True, null=True)

    trained_model = models.FileField(upload_to="models/", blank=True, null=True)
    training_acc = models.FloatField(blank=True, null=True)
    test_acc = models.FloatField(blank=True, null=True)

    class Meta:
        ordering = ("created",)