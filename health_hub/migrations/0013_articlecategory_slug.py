# Generated by Django 5.1.6 on 2025-04-12 13:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('health_hub', '0012_alter_articlepage_thumbnail'),
    ]

    operations = [
        migrations.AddField(
            model_name='articlecategory',
            name='slug',
            field=models.SlugField(max_length=255, null=True, unique=True),
        ),
    ]
