# Generated by Django 5.1.6 on 2025-03-07 06:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meal', '0003_mealitem_base_quantity_alter_mealitem_unit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mealitem',
            name='unit',
            field=models.CharField(choices=[('g', 'グラム'), ('ml', 'ミリリットル'), ('個', '個'), ('杯', '杯'), ('枚', '枚'), ('本', '本'), ('カップ', 'カップ'), ('人前', '人前')], max_length=10),
        ),
    ]
