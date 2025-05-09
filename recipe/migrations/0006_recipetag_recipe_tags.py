# Generated by Django 5.1.6 on 2025-03-23 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipe', '0005_recipe_difficulty'),
    ]

    operations = [
        migrations.CreateModel(
            name='RecipeTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, verbose_name='カテゴリ名')),
                ('description', models.TextField(blank=True, verbose_name='説明文')),
                ('slug', models.SlugField(unique=True, verbose_name='スラッグURL')),
            ],
        ),
        migrations.AddField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(related_name='recipes', to='recipe.recipetag', verbose_name='レシピカテゴリ'),
        ),
    ]
