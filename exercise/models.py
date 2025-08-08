from django.db import models
from django.conf import settings


# Create your models here.
class ExerciseCategory(models.Model):
    """
    エクササイズカテゴリモデル

    エクササイズの部位分類を管理します。
    """
    name = models.CharField(
        verbose_name='カテゴリ名',
        max_length=50,
        unique=True,
        help_text='カテゴリ名（胸、背中、肩など）'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'エクササイズカテゴリ'
        verbose_name_plural = 'エクササイズカテゴリ'

    def __str__(self):
        return self.name


class Exercise(models.Model):
    """
    エクササイズモデル（統合版）

    公式エクササイズとユーザーカスタムエクササイズを一つのテーブルで管理します。

    Attributes:
        name (CharField): エクササイズ名
        category (ForeignKey): カテゴリ
        description (TextField): 説明
        is_official (BooleanField): 公式エクササイズかどうか
        created_by (ForeignKey): 作成者（公式の場合はNull）
        created_at (DateTimeField): 作成日時
        updated_at (DateTimeField): 更新日時
    """
    name = models.CharField(
        verbose_name='エクササイズ名',
        max_length=255,
        help_text='エクササイズ名'
    )
    category = models.ForeignKey(
        ExerciseCategory,
        on_delete=models.CASCADE,
        related_name='exercises',
        verbose_name='カテゴリ',
        help_text='エクササイズのカテゴリ'
    )
    description = models.TextField(
        verbose_name='説明',
        help_text='エクササイズの説明'
    )
    is_official = models.BooleanField(
        verbose_name='公式エクササイズ',
        default=False,
        help_text='システム提供の公式エクササイズかどうか'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='custom_exercises',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='作成者',
        help_text='ユーザーが作成した場合の作成者（公式の場合はNull）'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'エクササイズ'
        verbose_name_plural = 'エクササイズ'
        # 公式エクササイズは重複可、ユーザーエクササイズは同一ユーザー・カテゴリ内で名前重複不可
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'category', 'created_by'],
                condition=models.Q(is_official=False),
                name='unique_user_exercise_per_category'
            )
        ]

    def clean(self):
        """バリデーション"""
        from django.core.exceptions import ValidationError

        # 公式エクササイズの場合、created_byはNullである必要がある
        if self.is_official and self.created_by is not None:
            raise ValidationError("公式エクササイズの場合、作成者は指定できません。")

        # ユーザーエクササイズの場合、created_byは必須
        if not self.is_official and self.created_by is None:
            raise ValidationError("ユーザーエクササイズの場合、作成者の指定が必要です。")

    @property
    def exercise_type(self):
        """エクササイズタイプを取得"""
        return 'official' if self.is_official else 'user'

    def __str__(self):
        type_str = "公式" if self.is_official else f"ユーザー({self.created_by.username})"
        return f"{self.name} ({self.category.name}) - {type_str}"


# 旧モデルは段階的削除のため、コメントアウトで残しておく
# class ExerciseMaster(models.Model):
#     """削除予定 - Exerciseモデルに統合"""
#     pass

# class UserExercise(models.Model):
#     """削除予定 - Exerciseモデルに統合"""
#     pass
