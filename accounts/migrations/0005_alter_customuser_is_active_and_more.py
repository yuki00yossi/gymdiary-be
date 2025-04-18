# Generated by Django 5.1.6 on 2025-04-12 12:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_emailverification'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='is_active',
            field=models.BooleanField(default=False, verbose_name='有効'),
        ),
        migrations.AlterField(
            model_name='emailverification',
            name='token',
            field=models.CharField(max_length=255),
        ),
    ]
