from django.db import models
from django.conf import settings


# Create your models here.
class WeightRecord(models.Model):
    """
    体重記録モデル

    ユーザーの体重と体脂肪率を記録するためのモデルです。
    同じ日付のデータが既に存在する場合は更新されます。

    Attributes:
        user (ForeignKey): 記録を所有するユーザー
        weight (FloatField): 体重（kg）
        fat (FloatField): 体脂肪率（%）、オプション
        record_date (DateTimeField): 記録日時
        created_at (DateTimeField): 作成日時（自動設定）
        updated_at (DateTimeField): 更新日時（自動更新）
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='weight_records',
        help_text='記録を所有するユーザー'
    )
    weight = models.FloatField(
        verbose_name='体重',
        help_text='体重（kg）'
    )
    fat = models.FloatField(
        verbose_name='体脂肪率',
        null=True,
        blank=True,
        help_text='体脂肪率（%）、オプション'
    )
    record_date = models.DateTimeField(
        verbose_name='日付',
        help_text='記録日時'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='作成日時（自動設定）'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='更新日時（自動更新）'
    )

    class Meta:
        """ メタ情報 """
        verbose_name = '体重'
        verbose_name_plural = '体重'
        ordering = ['-created_at']

    def __str__(self):
        return str(self.user.name)
