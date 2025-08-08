from django.db import models
from django.conf import settings


# Create your models here.
class MySet(models.Model):
    """
    マイセットモデル

    ユーザーが自分で作成したマイセットを管理します。
    マイセットは複数の種目とそれらのセット数をまとめて管理します。

    Attributes:
        user_id (ForeignKey): ユーザー
        name (CharField): セット名
        description (TextField): 説明
        created_at (DateTimeField): 作成日時
        updated_at (DateTimeField): 更新日時
    """
    user_id = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='mysets',
        on_delete=models.CASCADE,
        help_text='ユーザー'
    )
    name = models.CharField(
        verbose_name='セット名',
        max_length=255,
    )
    description = models.TextField(
        verbose_name='説明',
        null=True,
        blank=True,
        help_text='セットの説明'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='作成日時'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='更新日時'
    )


class MySetExercise(models.Model):
    """
    マイセット種目モデル

    マイセットに含まれる種目を管理します。
    種目は順番に並べて管理します。

    Attributes:
        myset_id (ForeignKey): マイセット
        exercise (ForeignKey): エクササイズ（移行中のため一時的にnullable）
        order (IntegerField): 順番
        created_at (DateTimeField): 作成日時
        updated_at (DateTimeField): 更新日時
    """
    myset_id = models.ForeignKey(
        MySet,
        related_name='exercises',
        on_delete=models.CASCADE,
        help_text='マイセット'
    )
    exercise = models.ForeignKey(
        'exercise.Exercise',
        related_name='myset_exercises',
        on_delete=models.CASCADE,
        null=True,  # 移行中のため一時的にnullable
        blank=True,
        help_text='エクササイズ'
    )
    order = models.IntegerField(
        verbose_name='順番',
        help_text='種目の順番'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def exercise_name(self):
        """エクササイズ名を取得"""
        if self.exercise:
            return self.exercise.name
        else:
            return "（未設定）"

    def __str__(self):
        return f"{self.exercise_name} (マイセット: {self.myset_id.name})"


class MySetExerciseSet(models.Model):
    """
    マイセット種目のセットモデル

    マイセット種目の実施セット情報を管理します。
    セットは順番に並べて管理します。

    Attributes:
        myset_exercise_id (ForeignKey): マイセット種目
        order (IntegerField): 順番
        weight (FloatField): 重量(kg)
        reps (IntegerField): 回数
        distance (FloatField): 距離
        distance_unit (CharField): 距離単位(m、kmなど・・)
        duration (IntegerField): 時間
    """
    myset_exercise_id = models.ForeignKey(
        MySetExercise,
        related_name='sets',
        on_delete=models.CASCADE,
        help_text='マイセット種目'
    )
    order = models.IntegerField(
        verbose_name='順番',
        help_text='セットの順番'
    )
    weight = models.FloatField(
        null=True, blank=True,
        verbose_name='重量(kg)'
    )
    reps = models.IntegerField(
        null=True, blank=True,
        verbose_name='回数'
    )
    distance = models.FloatField(
        null=True, blank=True,
        verbose_name='距離'
    )
    distance_unit = models.CharField(
        max_length=10, null=True, blank=True,
        verbose_name='距離単位'
    )
    duration = models.IntegerField(
        null=True, blank=True,
        verbose_name='時間'
    )
    duration_unit = models.CharField(
        max_length=10, null=True, blank=True,
        verbose_name='時間単位'
    )
    fat_burn = models.FloatField(
        null=True, blank=True,
        verbose_name='脂肪燃焼(kcal)'
    )
    memo = models.TextField(
        null=True, blank=True,
        verbose_name='メモ'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
