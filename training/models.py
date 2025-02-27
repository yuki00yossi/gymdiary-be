from django.db import models


# Create your models here.
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


def validate_positive(value):
    """ 0以下の値を許可しない """
    if value <= 0:
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
        validators=[validate_positive], null=True, blank=True)
    reps = models.IntegerField(
        validators=[validate_positive], null=True, blank=True)
    distance = models.FloatField(
        validators=[validate_positive], null=True, blank=True)
    time = models.CharField(max_length=10, blank=True, null=True)
    memo = models.TextField(blank=True, null=True)
