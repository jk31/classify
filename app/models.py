from django.db import models

import uuid
from annoying.fields import JSONField

# Create your models here.


class Dataset(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dataset = models.FileField(upload_to="models/")


class ClassificationModel(models.Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='models')
    variables = JSONField(blank=True, null=True)