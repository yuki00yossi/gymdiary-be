from django.db import models

from accounts.models import CustomUser
from meal.models import MealItem


# Create your models here.
class RecipeTag(models.Model):
    """レシピのタグ"""
    name = models.CharField(verbose_name="タグ名", max_length=64)
    description = models.TextField(verbose_name="説明文", blank=True)
    slug = models.SlugField(verbose_name="スラッグURL", unique=True)

    def __str__(self):
        return str(self.name)


class Recipe(models.Model):
    """レシピモデル"""
    title = models.CharField(verbose_name="レシピ名", max_length=256)
    difficulty = models.CharField(
        verbose_name="難易度", max_length=16,
        choices=(("簡単", "簡単"), ("中級", "中級"), ("上級", "上級"),), default="簡単")
    description = models.TextField(verbose_name="説明文")
    prep_time = models.IntegerField(verbose_name="調理時間")
    created_by = models.ForeignKey(
        CustomUser, null=True, blank=True, verbose_name="作成者",
        on_delete=models.SET_NULL, related_name='recipes')
    tags = models.ManyToManyField(
        RecipeTag, verbose_name="レシピカテゴリ", related_name="recipes")
    image = models.ImageField(
        upload_to='public/recipes', null=True, blank=True)

    size = models.IntegerField(verbose_name="何人前かを記録", default=1)
    # 栄養素に関するフィールド
    total_calories = models.IntegerField(verbose_name="カロリー", default=0)
    total_protein = models.IntegerField(verbose_name="たんぱく質", default=0)
    total_fat = models.IntegerField(verbose_name="脂質", default=0)
    total_carbs = models.IntegerField(verbose_name="炭水化物", default=0)

    def __str__(self):
        return str(self.title)


class RecipeIngredient(models.Model):
    """レシピの材料"""
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="ingredients")
    meal_item = models.ForeignKey(MealItem, on_delete=models.CASCADE)
    quantity = models.FloatField(verbose_name="使用量")

    def __str__(self):
        return f"{self.recipe.title} - {self.meal_item.name}"


class RecipeStep(models.Model):
    """レシピの作成手順"""
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="steps")
    step_number = models.IntegerField(verbose_name="手重番号")
    description = models.TextField(verbose_name="手順の文章")
    image = models.ImageField(
        upload_to='public/recipes/steps', null=True, blank=True)

    class Meta:
        """手順番号順に表示されるようにする"""
        ordering = ['step_number']

    def __str__(self):
        return f"Step {self.step_number} for {self.recipe.title}"


class RecipeTip(models.Model):
    """レシピのコツ"""
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="tips")
    tip_text = models.TextField(verbose_name="コツの文章")

    def __str__(self):
        return f"Tip for {self.recipe.title}"


class RecipeReview(models.Model):
    """レシピのレビュー"""
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(
        CustomUser, null=True, blank=True, on_delete=models.SET_NULL)
    comment = models.TextField(verbose_name="コメント")
    created_at = models.DateTimeField(verbose_name="作成日", auto_now_add=True)

    def __str__(self):
        return f"{self.recipe.title}:{self.comment}"
