from django.db import models
from django.conf import settings


# Create your models here.
class WeightRecord(models.Model):
    """ 体重記録モデル """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='weight_records')
    weight = models.FloatField(verbose_name='体重')
    fat = models.FloatField(verbose_name='体脂肪率', null=True, blank=True)
    record_date = models.DateTimeField(verbose_name='日付')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """ メタ情報 """
        verbose_name = '体重'
        verbose_name_plural = '体重'
        ordering = ['-created_at']

    def __str__(self):
        return str(self.user.name)
