from django.db import models
from django.conf import settings

# Create your models here.
class WorkoutSession(models.Model):
    """
    トレーニングセッションモデル

    ユーザーのトレーニングセッションを記録するためのモデルです。
    複数種目をまとめて管理します。

    Attributes:
        user_id (ForeignKey): ユーザー
        name (CharField): セッション名
        date (DateField): 日付
        memo (TextField): メモ
        created_at (DateTimeField): 作成日時
        updated_at (DateTimeField): 更新日時
    """
    user_id = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='workouts',
        on_delete=models.CASCADE,
        help_text='ユーザー'
    )
    name = models.CharField(
        verbose_name='セッション名',
        max_length=255,
        help_text='セッション名（胸トレーニングなど）'
    )
    date = models.DateField(
        verbose_name='日付',
        help_text='トレーニング日'
    )
    memo = models.TextField(
        verbose_name='メモ',
        null=True,
        blank=True,
        help_text='トレーニングのメモ'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='作成日時'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='更新日時'
    )


class WorkoutExercise(models.Model):
    """
    トレーニング種目モデル

    トレーニングセッションに含まれる種目を管理します。
    種目は順番に並べて管理します。

    Attributes:
        workout_session_id (ForeignKey): トレーニングセッション
        exercise (ForeignKey): エクササイズ（移行中のため一時的にnullable）
        order (IntegerField): 順番
        created_at (DateTimeField): 作成日時
        updated_at (DateTimeField): 更新日時
    """
    workout_session_id = models.ForeignKey(
        'WorkoutSession',
        related_name='workout_exercises',
        on_delete=models.CASCADE,
        help_text='トレーニングセッション'
    )
    exercise = models.ForeignKey(
        'exercise.Exercise',
        related_name='workout_exercises',
        on_delete=models.CASCADE,
        null=True,  # 移行中のため一時的にnullable
        blank=True,
        help_text='エクササイズ'
    )
    order = models.IntegerField(
        verbose_name='順番',
        help_text='種目の順番'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='作成日時'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='更新日時'
    )

    @property
    def exercise_name(self):
        """エクササイズ名を取得"""
        if self.exercise:
            return self.exercise.name
        else:
            return "（未設定）"

    def __str__(self):
        return f"{self.exercise_name} (セッション: {self.workout_session_id.name})"


class WorkoutExerciseSet(models.Model):
    """
    トレーニング種目のセットモデル

    トレーニング種目の実施セット情報を管理します。
    セットは順番に並べて管理します。

    Attributes:
        workout_exercise_id (ForeignKey): トレーニング種目
        weight (FloatField): 重量(kg)
        reps (IntegerField): 回数
        distance (FloatField): 距離
        distance_unit (CharField): 距離単位(m、kmなど・・)
        duration (IntegerField): 時間
        duration_unit (CharField): 時間単位(分、秒など・・)
        fat_burn (IntegerField): 脂肪燃焼(kcal)
    """
    workout_exercise_id = models.ForeignKey(
        WorkoutExercise,
        related_name='workout_exercise_sets',
        on_delete=models.CASCADE,
        help_text='トレーニング種目'
    )
    order = models.IntegerField(
        verbose_name='順番',
        help_text='セットの順番'
    )
    weight = models.FloatField(
        null=True,
        blank=True,
        verbose_name='重量(kg)',
        help_text='重量(kg)'
    )
    reps = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='回数',
        help_text='回数'
    )
    distance = models.FloatField(
        null=True,
        blank=True,
        verbose_name='距離',
        help_text='距離'
    )
    distance_unit = models.CharField(
        null=True,
        blank=True,
        max_length=10,
        verbose_name='距離単位',
        help_text='距離単位'
    )
    duration = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='時間',
        help_text='時間'
    )
    duration_unit = models.CharField(
        null=True,
        blank=True,
        max_length=10,
        verbose_name='時間単位',
        help_text='時間単位'
    )
    fat_burn = models.FloatField(
        null=True,
        blank=True,
        verbose_name='脂肪燃焼(kcal)',
        help_text='脂肪燃焼(kcal)'
    )
    memo = models.TextField(
        null=True,
        blank=True,
        verbose_name='メモ',
        help_text='セットのメモ'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='作成日時'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='更新日時'
    )
