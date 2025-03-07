from django.db import models
from django.conf import settings
from accounts.models import CustomUser


class MealItem(models.Model):
    """ 共有可能な食品データ """
    name = models.CharField(max_length=100, unique=False)
    calories = models.FloatField()
    protein = models.FloatField()
    fat = models.FloatField()
    carbs = models.FloatField()
    unit = models.CharField(max_length=10, choices=[
        ("g", "グラム"), ("ml", "ミリリットル"), ("個", "個"), ("杯", "杯"),
        ("枚", "枚"), ("本", "本"), ("カップ", "カップ"), ("人前", "人前"),
    ])

    base_quantity = models.FloatField(default=100)  # 100g, 1個, 200mlなど
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="meal_items")

    class Meta:
        """ メタ情報 """
        verbose_name = '食品'
        verbose_name_plural = '食品'

    def __str__(self):
        return str(self.name)


class MealRecord(models.Model):
    """ ユーザーの食事記録 """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="meals")
    date = models.DateField()
    time_of_day = models.CharField(
        max_length=10,
        choices=[("朝食", "朝食"), ("昼食", "昼食"), ("夕食", "夕食"), ("間食", "間食")]
    )
    photo = models.ImageField(upload_to="meals/", null=True, blank=True)  # 画像はNULL許可

    class Meta:
        """ メタ情報 """
        verbose_name = '食事記録'
        verbose_name_plural = '食事記録'

    def __str__(self):
        return str(f"{self.user.username} - {self.date} {self.time_of_day}")


class MealRecordItem(models.Model):
    """ 食事記録の詳細（食品ごとの摂取量） """
    meal_record = models.ForeignKey(MealRecord, on_delete=models.CASCADE, related_name="meal_items")
    meal_item = models.ForeignKey(MealItem, on_delete=models.CASCADE)
    quantity = models.FloatField()
    unit = models.CharField(max_length=10)

    class Meta:
        """ メタ情報 """
        verbose_name = '食事記録の詳細'
        verbose_name_plural = '食事記録の詳細'

    def __str__(self):
        return str(f"{self.meal_record} - {self.meal_item.name} {self.quantity}{self.unit}")
