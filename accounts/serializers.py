from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser, UserRole


class UserSerializer(serializers.ModelSerializer):
    """ ユーザー情報のシリアライザー """
    class Meta:
        """ メタ情報 """
        model = CustomUser
        fields = ('id', 'username', 'name')
        read_only_fields = ('id',)


class UserRoleSerializer(serializers.ModelSerializer):
    """ ユーザーロールのシリアライザー """
    class Meta:
        """ メタ情報 """
        model = UserRole
        fields = ('id', 'user', 'role')


class UserRegisterSerializer(serializers.ModelSerializer):
    """ 新規会員登録用のシリアライザー """
    password = serializers.CharField(write_only=True, min_length=6)
    role = serializers.ChoiceField(
        choices=UserRole.ROLE_CHOICES, write_only=True, required=False)

    class Meta:
        """ メタ情報 """
        model = CustomUser
        fields = ('username', 'name', 'password', 'role')

    def create(self, validated_data):
        """ ユーザー作成し、選択したロールを割り当てる """
        # 役割はトレーナー用アプリを作る時に再度検討する
        # role = validated_data.pop('role')
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            name=validated_data['name'],
            password=validated_data['password'],
        )
        # UserRole.objects.create(user=user, role=role)
        return user


class UserLoginSerializer(serializers.Serializer):
    """ ログインAPI用のシリアライザー """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, min_length=6)

    def validate(self, attrs):
        """ 認証チェック """
        user = authenticate(
            username=attrs['username'], password=attrs['password'])
        if not user:
            raise serializers.ValidationError('認証失敗： ユーザー名もしくはパスワードが正しくありません')
        return user
