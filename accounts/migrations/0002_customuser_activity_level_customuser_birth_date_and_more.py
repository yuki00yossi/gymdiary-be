# Generated by Django 5.1.6 on 2025-03-30 13:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='activity_level',
            field=models.FloatField(blank=True, null=True, verbose_name='活動レベル'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='birth_date',
            field=models.DateField(blank=True, null=True, verbose_name='生年月日'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='height',
            field=models.FloatField(blank=True, null=True, verbose_name='身長 (cm)'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='sex',
            field=models.CharField(choices=[('male', '男性'), ('female', '女性')], default='male', max_length=10, verbose_name='性別'),
        ),
    ]
