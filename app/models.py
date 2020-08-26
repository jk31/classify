from django.db import models

import uuid
from annoying.fields import JSONField

# Create your models here.


class Dataset(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dataset = models.FileField(upload_to="models/")


class ClassificationModel(models.Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='models')
    training_columns = JSONField(blank=True, null=True)
    variables = JSONField(blank=True, null=True)
    goal = models.CharField(max_length=100, blank=True, null=True)
    trained_model = models.FileField(upload_to="models/", blank=True, null=True)
    training_acc = models.CharField(max_length=10, blank=True, null=True)
    test_acc = models.CharField(max_length=10, blank=True, null=True)