# Generated by Django 5.1.6 on 2025-03-04 00:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meal', '0002_mealitem_created_by_alter_mealitem_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='mealitem',
            name='base_quantity',
            field=models.FloatField(default=100),
        ),
        migrations.AlterField(
            model_name='mealitem',
            name='unit',
            field=models.CharField(choices=[('g', 'グラム'), ('ml', 'ミリリットル'), ('個', '個'), ('杯', '杯')], max_length=10),
        ),
    ]
