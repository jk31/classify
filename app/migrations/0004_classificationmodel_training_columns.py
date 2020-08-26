# Generated by Django 3.0.8 on 2020-08-26 15:21

import annoying.fields
from django.db import migrations
import json


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_auto_20200825_1615'),
    ]

    operations = [
        migrations.AddField(
            model_name='classificationmodel',
            name='training_columns',
            field=annoying.fields.JSONField(blank=True, deserializer=json.loads, null=True, serializer=annoying.fields.dumps),
        ),
    ]