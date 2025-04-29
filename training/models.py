from django.db import models


# Create your models here.
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


def validate_positive(value):
    """ 0以下の値を許可しない """
    if value <= 0:
        raise ValidationError("0より大きい値を入力してください。")


def validate_non_negative(value):
    """ 0以上の値のみ許可（負の値は禁止） """
    if value < 0:
        raise ValidationError("0より大きい値を入力してください。")


class TrainingSession(models.Model):
    """ 1回のワークアウト（セッション） """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="training_sessions")
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]


class Workout(models.Model):
    """ エクササイズ（種目ごとの記録） """
    session = models.ForeignKey(TrainingSession, on_delete=models.CASCADE, related_name="workouts")
    menu = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=[("weight", "重量"), ("distance", "距離")])
    unit = models.CharField(max_length=10)  # kg, km など
    memo = models.TextField(blank=True, null=True)


class WorkoutSet(models.Model):
    """ セットごとの記録 """
    workout = models.ForeignKey(
        Workout, on_delete=models.CASCADE, related_name="sets")
    weight = models.FloatField(
        validators=[validate_non_negative], null=True, blank=True)
    reps = models.IntegerField(
        validators=[validate_positive], null=True, blank=True)
    distance = models.FloatField(
        validators=[validate_non_negative], null=True, blank=True)
    time = models.CharField(max_length=10, blank=True, null=True)
    memo = models.TextField(blank=True, null=True)


# --- マイセットテンプレート関連 ---
class MySet(models.Model):
    """ ユーザー専用またはトレーナー提供のトレーニングテンプレート（マイセット） """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="my_sets",
        help_text="このマイセットを使うユーザー"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_my_sets",
        help_text="このマイセットを作成したユーザー（トレーナーまたは本人）"
    )
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.user.username})"


class MyWorkout(models.Model):
    myset = models.ForeignKey(MySet, on_delete=models.CASCADE, related_name="workouts")
    menu = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=[("weight", "重量"), ("distance", "距離")])
    unit = models.CharField(max_length=10)
    memo = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.menu} ({self.myset.name})"


class MyWorkoutSet(models.Model):
    workout = models.ForeignKey(MyWorkout, on_delete=models.CASCADE, related_name="sets")
    weight = models.FloatField(validators=[validate_non_negative], null=True, blank=True)
    reps = models.IntegerField(validators=[validate_positive], null=True, blank=True)
    distance = models.FloatField(validators=[validate_positive], null=True, blank=True)
    time = models.CharField(max_length=10, blank=True, null=True)
    memo = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.workout.menu} ({self.workout.myset.name})"


# --- マイセット記録（履歴）関連 ---
class MySetSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="my_set_sessions")
    myset = models.ForeignKey(MySet, on_delete=models.CASCADE, related_name="sessions")
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.myset.name} ({self.user.username}) - {self.date}"


class MySetWorkoutRecord(models.Model):
    session = models.ForeignKey(MySetSession, on_delete=models.CASCADE, related_name="workouts")
    menu = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=[("weight", "重量"), ("distance", "距離")])
    unit = models.CharField(max_length=10)
    memo = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.menu} ({self.session.myset.name}) - {self.session.date}"


class MySetWorkoutSetRecord(models.Model):
    workout = models.ForeignKey(MySetWorkoutRecord, on_delete=models.CASCADE, related_name="sets")
    weight = models.FloatField(validators=[validate_non_negative], null=True, blank=True)
    reps = models.IntegerField(validators=[validate_positive], null=True, blank=True)
    distance = models.FloatField(validators=[validate_positive], null=True, blank=True)
    time = models.CharField(max_length=10, blank=True, null=True)
    memo = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.workout.menu} ({self.workout.session.myset.name}) - {self.workout.session.date}"
