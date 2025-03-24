import uuid
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone


class TrainerProfile(models.Model):
    """トレーナー情報"""
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    experience = models.IntegerField(default=0)
    certifications = models.TextField(blank=True)
    rating = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)


class TrainingPlan(models.Model):
    """トレーニングプラン（単発 & 月額）"""
    PLAN_TYPE_CHOICES = [
        ("one_time", "単発"),
        ("subscription", "月額"),
    ]

    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    trainer = models.ForeignKey(TrainerProfile, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.IntegerField()
    duration = models.IntegerField()
    is_available = models.BooleanField(default=True)
    plan_type = models.CharField(choices=PLAN_TYPE_CHOICES, max_length=15, default="one_time")
    stripe_price_id = models.CharField(max_length=255, blank=True, null=True)  # Stripeの価格ID
    created_at = models.DateTimeField(auto_now_add=True)


class TrainingApplication(models.Model):
    """トレーニング申し込み（単発 & 月額）"""
    STATUS_CHOICES = [
        ("pending", "仮予約"),
        ("approved", "承認済み（支払い待ち）"),
        ("confirmed", "確定"),
        ("active", "月額契約中"),
        ("payment_failed", "支払い失敗"),
        ("canceled", "キャンセル"),
    ]

    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    trainer = models.ForeignKey(TrainerProfile, on_delete=models.CASCADE)
    plan = models.ForeignKey(TrainingPlan, on_delete=models.CASCADE)
    status = models.CharField(choices=STATUS_CHOICES, max_length=20, default="pending")
    stripe_subscription_id = models.CharField(max_length=255, blank=True, null=True)  # 月額用
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=timezone.now)
