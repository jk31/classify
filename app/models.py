from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

import uuid
from annoying.fields import JSONField

from classify.storage_backends import PublicMediaStorage, PrivateMediaStorage
from .managers import CustomUserManager


# Create your models here.

class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email


def validate_dataset_size(dataset):
    if dataset.size > 1048576:
        raise ValidationError("Max size of file is 10 mb.")

class Dataset(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="owner_datasets", on_delete=models.CASCADE, blank=True, null=True)
    dataset = models.FileField(storage=PrivateMediaStorage(), upload_to="datasets/", validators=[FileExtensionValidator(allowed_extensions=["xlsx"]), validate_dataset_size])

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created",)

    def __str__(self):
        return self.name


class ClassificationModel(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="owner_models", on_delete=models.CASCADE, blank=True, null=True)
    dataset = models.ForeignKey(Dataset, on_delete=models.SET_NULL, related_name='models', null=True)

    created = models.DateTimeField(auto_now_add=True)
    saved = models.BooleanField(default=False)

    training_columns = JSONField(blank=True, null=True)
    variables = JSONField(blank=True, null=True)
    goal = models.CharField(max_length=100, blank=True, null=True)

    trained_model = models.FileField(storage=PrivateMediaStorage(), upload_to="models/", blank=True, null=True)
    training_acc = models.FloatField(blank=True, null=True)
    test_acc = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"{self.dataset} - {self.created}"

    class Meta:
        ordering = ("-created",)