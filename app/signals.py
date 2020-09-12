from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from django.core.mail import send_mail

from app.models import Dataset

@receiver(post_save, sender=Dataset)
def dataset_upload_signal(sender, instance, **kwargs):
    send_mail(
        "Classify: Dateset Created",
        "New dataset uploaded.",
        None,
        ["jaroslaw@kornowicz.com"]
        )

@receiver(post_save, sender=User)
def user_created_signal(sender, instance, **kwargs):
        send_mail(
        "Classify: New user created",
        "A new registration",
        None,
        ["jaroslaw@kornowicz.com"]
        )

