# Generated by Django 5.1.6 on 2025-03-08 05:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meal', '0004_alter_mealitem_unit'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mealrecord',
            name='photo',
        ),
        migrations.AddField(
            model_name='mealrecord',
            name='photo_key',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
    ]
