# Generated by Django 5.1.6 on 2025-03-22 22:58

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('meal', '0005_remove_mealrecord_photo_mealrecord_photo_key'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=256, verbose_name='レシピ名')),
                ('description', models.TextField(verbose_name='説明文')),
                ('prep_time', models.IntegerField(verbose_name='調理時間')),
                ('image', models.ImageField(blank=True, null=True, upload_to='public/recipes/')),
                ('size', models.IntegerField(default=1, verbose_name='何人前かを記録')),
                ('total_calories', models.IntegerField(default=0, verbose_name='カロリー')),
                ('total_protein', models.IntegerField(default=0, verbose_name='たんぱく質')),
                ('total_fat', models.IntegerField(default=0, verbose_name='脂質')),
                ('total_carbs', models.IntegerField(default=0, verbose_name='炭水化物')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='recipes', to=settings.AUTH_USER_MODEL, verbose_name='作成者')),
            ],
        ),
        migrations.CreateModel(
            name='RecipeIngredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.FloatField(verbose_name='使用量')),
                ('meal_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='meal.mealitem')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredients', to='recipe.recipe')),
            ],
        ),
        migrations.CreateModel(
            name='RecipeReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField(verbose_name='コメント')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='作成日')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='recipe.recipe')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='RecipeStep',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('step_number', models.IntegerField(verbose_name='手重番号')),
                ('description', models.TextField(verbose_name='手順の文章')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='steps', to='recipe.recipe')),
            ],
            options={
                'ordering': ['step_number'],
            },
        ),
        migrations.CreateModel(
            name='RecipeTip',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tip_text', models.TextField(verbose_name='コツの文章')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tips', to='recipe.recipe')),
            ],
        ),
    ]
