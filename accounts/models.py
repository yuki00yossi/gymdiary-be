import re
from django.core.exceptions import ValidationError
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin)
from django.db import models


def validate_username(value):
    if not re.match(r"[a-zA-Z0-9_.]+$", value):
        raise ValidationError("ユーザー名は半角英数字、アンダースコア (_) 、ドット (.) のみ使用できます。")


# Create your models here.
class CustomUserManager(BaseUserManager):
    """ カスタムのユーザーマネージャー """
    def create_user(self, username, name, password=None):
        """ユーザーを作成する

        Args:
            username (string): ユーザー名
            password (string, optional): パスワード。デフォルトはNone

        Raises:
            ValueError: 必須エラー

        Returns:
            CustomUser: CustomUserインスタンス
        """
        if not username:
            raise ValueError('ユーザー名は必須です')
        user = self.model(username=username)
        user.name = name
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, name, password):
        """ 管理者ユーザーを作成する

        Args:
            username (string): ユーザー名
            password (string): パスワード

        Returns:
            CustomUser: CustomUserインスタンス
        """
        user = self.create_user(username, name, password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """ Gym Diaryのカスタムユーザークラス """
    username = models.CharField(
        verbose_name='ユーザー名', max_length=50,
        unique=True, validators=[validate_username,],)
    name = models.CharField(verbose_name='表示名', max_length=50)
    is_active = models.BooleanField(verbose_name='有効', default=True)
    is_staff = models.BooleanField(verbose_name='スタッフ権限', default=False)

    created_at = models.DateTimeField(verbose_name='登録日', auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['name',]

    class Meta:
        """ メタ情報 """
        verbose_name = 'ユーザー'
        verbose_name_plural = 'ユーザー'

    def __str__(self):
        return str(self.username)


class UserRole(models.Model):
    """ ユーザーのロール、トレーナーか一般会員か """
    ROLE_CHOICES = (
        ('trainer', 'トレーナー'),
        ('member', '一般会員'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='roles')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    class Meta:
        """ メタ情報 """
        unique_together = ('user', 'role')
        verbose_name = 'ユーザー種別'
        verbose_name_plural = 'ユーザー種別'

    def __str__(self):
        return str(self.user.username+ ': ' + self.role)
