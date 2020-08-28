# Generated by Django 3.0.8 on 2020-08-28 14:48

import annoying.fields
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import json


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Dataset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('dataset', models.FileField(upload_to='datasets/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['xlsx'])])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='owner_datasets', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-created',),
            },
        ),
        migrations.CreateModel(
            name='ClassificationModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('saved', models.BooleanField(default=False)),
                ('training_columns', annoying.fields.JSONField(blank=True, deserializer=json.loads, null=True, serializer=annoying.fields.dumps)),
                ('variables', annoying.fields.JSONField(blank=True, deserializer=json.loads, null=True, serializer=annoying.fields.dumps)),
                ('goal', models.CharField(blank=True, max_length=100, null=True)),
                ('trained_model', models.FileField(blank=True, null=True, upload_to='models/')),
                ('training_acc', models.FloatField(blank=True, null=True)),
                ('test_acc', models.FloatField(blank=True, null=True)),
                ('dataset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='models', to='app.Dataset')),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='owner_models', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-created',),
            },
        ),
    ]
