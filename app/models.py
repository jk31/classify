from django.db import models

from annoying.fields import JSONField

# Create your models here.

class ClassificationModel(models.Model):
    data = JSONField(blank=True, null=True)