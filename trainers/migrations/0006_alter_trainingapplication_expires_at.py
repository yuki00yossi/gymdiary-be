# Generated by Django 5.1.6 on 2025-03-21 11:25

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trainers', '0005_alter_trainingapplication_expires_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trainingapplication',
            name='expires_at',
            field=models.DateTimeField(default=datetime.datetime(2025, 3, 23, 11, 25, 31, 856066, tzinfo=datetime.timezone.utc)),
        ),
    ]
