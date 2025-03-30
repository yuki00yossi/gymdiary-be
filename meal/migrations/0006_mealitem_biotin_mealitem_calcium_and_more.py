# Generated by Django 5.1.6 on 2025-03-30 13:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meal', '0005_remove_mealrecord_photo_mealrecord_photo_key'),
    ]

    operations = [
        migrations.AddField(
            model_name='mealitem',
            name='biotin',
            field=models.FloatField(blank=True, null=True, verbose_name='ビオチン（μg）'),
        ),
        migrations.AddField(
            model_name='mealitem',
            name='calcium',
            field=models.FloatField(blank=True, null=True, verbose_name='カルシウム（mg）'),
        ),
        migrations.AddField(
            model_name='mealitem',
            name='cholesterol',
            field=models.FloatField(blank=True, null=True, verbose_name='コレステロール（mg）'),
        ),
        migrations.AddField(
            model_name='mealitem',
            name='chromium',
            field=models.FloatField(blank=True, null=True, verbose_name='クロム（μg）'),
        ),
        migrations.AddField(
            model_name='mealitem',
            name='copper',
            field=models.FloatField(blank=True, null=True, verbose_name='銅（mg）'),
        ),
        migrations.AddField(
            model_name='mealitem',
            name='dietary_fiber',
            field=models.FloatField(blank=True, null=True, verbose_name='食物繊維（g）'),
        ),
        migrations.AddField(
            model_name='mealitem',
            name='folic_acid',
            field=models.FloatField(blank=True, null=True, verbose_name='葉酸（μg）'),
        ),
        migrations.AddField(
            model_name='mealitem',
            name='iodine',
            field=models.FloatField(blank=True, null=True, verbose_name='ヨウ素（μg）'),
        ),
        migrations.AddField(
            model_name='mealitem',
            name='iron',
            field=models.FloatField(blank=True, null=True, verbose_name='鉄（mg）'),
        ),
        migrations.AddField(
            model_name='mealitem',
            name='magnesium',
            field=models.FloatField(blank=True, null=True, verbose_name='マグネシウム（mg）'),
        ),
        migrations.AddField(
            model_name='mealitem',
            name='manganese',
            field=models.FloatField(blank=True, null=True, verbose_name='マンガン（mg）'),
        ),
        migrations.AddField(
            model_name='mealitem',
            name='molybdenum',
            field=models.FloatField(blank=True, null=True, verbose_name='モリブデン（μg）'),
        ),
        migrations.AddField(
            model_name='mealitem',
            name='niacin',
            field=models.FloatField(blank=True, null=True, verbose_name='ナイアシン（mgNE）'),
        ),
        migrations.AddField(
            model_name='mealitem',
            name='pantothenic_acid',
            field=models.FloatField(blank=True, null=True, verbose_name='パントテン酸（mg）'),
        ),
        migrations.AddField(
            model_name='mealitem',
            name='phosphorus',
            field=models.FloatField(blank=True, null=True, verbose_name='リン（mg）'),
        ),
        migrations.AddField(
            model_name='mealitem',
            name='potassium',
            field=models.FloatField(blank=True, null=True, verbose_name='カリウム（mg）'),
        ),
        migrations.AddField(
            model_name='mealitem',
            name='salt_equivalent',
            field=models.FloatField(blank=True, null=True, verbose_name='食塩相当量（g）'),
        ),
        migrations.AddField(
            model_name='mealitem',
            name='selenium',
            field=models.FloatField(blank=True, null=True, verbose_name='セレン（μg）'),
        ),
        migrations.AddField(
            model_name='mealitem',
            name='sodium',
            field=models.FloatField(blank=True, null=True, verbose_name='ナトリウム（g）'),
        ),
        migrations.AddField(
            model_name='mealitem',
            name='vitamin_a',
            field=models.FloatField(blank=True, null=True, verbose_name='ビタミンA（μgRAE）'),
        ),
        migrations.AddField(
            model_name='mealitem',
            name='vitamin_b1',
            field=models.FloatField(blank=True, null=True, verbose_name='ビタミンB1（mg）'),
        ),
        migrations.AddField(
            model_name='mealitem',
            name='vitamin_b12',
            field=models.FloatField(blank=True, null=True, verbose_name='ビタミンB12（μg）'),
        ),
        migrations.AddField(
            model_name='mealitem',
            name='vitamin_b2',
            field=models.FloatField(blank=True, null=True, verbose_name='ビタミンB2（mg）'),
        ),
        migrations.AddField(
            model_name='mealitem',
            name='vitamin_b6',
            field=models.FloatField(blank=True, null=True, verbose_name='ビタミンB6（mg）'),
        ),
        migrations.AddField(
            model_name='mealitem',
            name='vitamin_c',
            field=models.FloatField(blank=True, null=True, verbose_name='ビタミンC（mg）'),
        ),
        migrations.AddField(
            model_name='mealitem',
            name='vitamin_d',
            field=models.FloatField(blank=True, null=True, verbose_name='ビタミンD（μg）'),
        ),
        migrations.AddField(
            model_name='mealitem',
            name='vitamin_e',
            field=models.FloatField(blank=True, null=True, verbose_name='ビタミンE（mg）'),
        ),
        migrations.AddField(
            model_name='mealitem',
            name='vitamin_k',
            field=models.FloatField(blank=True, null=True, verbose_name='ビタミンK（μg）'),
        ),
        migrations.AddField(
            model_name='mealitem',
            name='zinc',
            field=models.FloatField(blank=True, null=True, verbose_name='亜鉛（mg）'),
        ),
    ]
