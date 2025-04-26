from django.db import models


from django.db import models
from accounts.models import CustomUser  # Userモデルのパスに合わせて調整してね


class TrainerProfile(models.Model):
    """ トレーナープロフィールモデル """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='trainer_profile')
    bio = models.TextField(blank=True, verbose_name="自己紹介")
    specialties = models.JSONField(default=list, verbose_name="得意分野（ジャンル）", help_text="例: ['筋トレ', 'ピラティス']")
    certifications = models.JSONField(default=list, verbose_name="保有資格", help_text="例: ['NSCA-CPT', 'JATI-ATI']")
    career = models.TextField(blank=True, verbose_name="経歴・実績")
    intro_video_url = models.URLField(blank=True, null=True, verbose_name="紹介動画URL")
    is_public = models.BooleanField(default=False, verbose_name="公開フラグ")

    def __str__(self):
        return f"{self.user.name}"


class InterviewSchedule(models.Model):
    """ 面談予約スケジュールモデル """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='interview_schedule')
    date = models.DateField()
    time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
