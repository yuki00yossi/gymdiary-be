from rest_framework import serializers
from django.db.models import Count, Q
from .models import ExerciseCategory, Exercise


class ExerciseCategorySerializer(serializers.ModelSerializer):
    """エクササイズカテゴリシリアライザー"""

    class Meta:
        model = ExerciseCategory
        fields = ('id', 'name')


class ExerciseSerializer(serializers.ModelSerializer):
    """エクササイズシリアライザー（統合版）"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    exercise_type = serializers.CharField(read_only=True)

    class Meta:
        model = Exercise
        fields = ('id', 'name', 'description', 'category', 'category_name', 'exercise_type', 'is_official', 'created_at', 'updated_at')
        read_only_fields = ('id', 'is_official', 'created_at', 'updated_at')

    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("エクササイズ名を入力してください。")
        return value.strip()

    def create(self, validated_data):
        """ユーザーエクササイズを作成"""
        request = self.context.get("request")
        return Exercise.objects.create(
            created_by=request.user,
            is_official=False,
            **validated_data
        )

    def update(self, instance, validated_data):
        """エクササイズを更新（公式エクササイズは更新不可）"""
        if instance.is_official:
            raise serializers.ValidationError("公式エクササイズは更新できません。")

        return super().update(instance, validated_data)


class ExerciseListSerializer(serializers.Serializer):
    """エクササイズ一覧レスポンス用シリアライザー"""
    name = serializers.CharField()
    description = serializers.CharField()
    id = serializers.IntegerField()
    type = serializers.CharField()  # 'official' or 'user'