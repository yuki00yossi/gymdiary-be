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

    # --- 栄養素の拡張 ---
    vitamin_a = models.FloatField("ビタミンA（μgRAE）", null=True, blank=True)
    vitamin_d = models.FloatField("ビタミンD（μg）", null=True, blank=True)
    vitamin_e = models.FloatField("ビタミンE（mg）", null=True, blank=True)
    vitamin_k = models.FloatField("ビタミンK（μg）", null=True, blank=True)
    vitamin_b1 = models.FloatField("ビタミンB1（mg）", null=True, blank=True)
    vitamin_b2 = models.FloatField("ビタミンB2（mg）", null=True, blank=True)
    niacin = models.FloatField("ナイアシン（mgNE）", null=True, blank=True)
    vitamin_b6 = models.FloatField("ビタミンB6（mg）", null=True, blank=True)
    vitamin_b12 = models.FloatField("ビタミンB12（μg）", null=True, blank=True)
    folic_acid = models.FloatField("葉酸（μg）", null=True, blank=True)
    pantothenic_acid = models.FloatField("パントテン酸（mg）", null=True, blank=True)
    biotin = models.FloatField("ビオチン（μg）", null=True, blank=True)
    vitamin_c = models.FloatField("ビタミンC（mg）", null=True, blank=True)
    sodium = models.FloatField("ナトリウム（g）", null=True, blank=True)
    potassium = models.FloatField("カリウム（mg）", null=True, blank=True)
    calcium = models.FloatField("カルシウム（mg）", null=True, blank=True)
    magnesium = models.FloatField("マグネシウム（mg）", null=True, blank=True)
    phosphorus = models.FloatField("リン（mg）", null=True, blank=True)
    iron = models.FloatField("鉄（mg）", null=True, blank=True)
    zinc = models.FloatField("亜鉛（mg）", null=True, blank=True)
    copper = models.FloatField("銅（mg）", null=True, blank=True)
    manganese = models.FloatField("マンガン（mg）", null=True, blank=True)
    iodine = models.FloatField("ヨウ素（μg）", null=True, blank=True)
    selenium = models.FloatField("セレン（μg）", null=True, blank=True)
    chromium = models.FloatField("クロム（μg）", null=True, blank=True)
    molybdenum = models.FloatField("モリブデン（μg）", null=True, blank=True)
    cholesterol = models.FloatField("コレステロール（mg）", null=True, blank=True)
    dietary_fiber = models.FloatField("食物繊維（g）", null=True, blank=True)
    salt_equivalent = models.FloatField("食塩相当量（g）", null=True, blank=True)

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
    photo_key = models.CharField(null=True, blank=True, max_length=256)  # 画像はNULL許可

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
