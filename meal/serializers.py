from rest_framework import serializers
from accounts.utils import generate_presigned_url  # S3の署名付きURLを生成
from .models import MealItem, MealRecord, MealRecordItem


class MealItemSerializer(serializers.ModelSerializer):
    """ 食品データ（ユーザーが追加可能） """

    class Meta:
        model = MealItem
        fields = ("id", "name", "calories", "protein", "fat", "carbs", "unit")

    def validate_calories(self, value):
        if value < 0:
            raise serializers.ValidationError("カロリーは0以上にしてください。")
        return value

    def validate_protein(self, value):
        if value < 0:
            raise serializers.ValidationError("タンパク質は0以上にしてください。")
        return value

    def validate_fat(self, value):
        if value < 0:
            raise serializers.ValidationError("脂質は0以上にしてください。")
        return value

    def validate_carbs(self, value):
        if value < 0:
            raise serializers.ValidationError("炭水化物は0以上にしてください。")
        return value

    def create(self, validated_data):
        """ 食品データを登録（作成者を記録） """
        user = self.context["request"].user
        return MealItem.objects.create(created_by=user, **validated_data)


class MealRecordItemSerializer(serializers.ModelSerializer):
    """ 食事記録アイテム（摂取量を管理） """
    meal_item = MealItemSerializer(read_only=True)
    meal_item_id = serializers.PrimaryKeyRelatedField(
        queryset=MealItem.objects.all(), source="meal_item", write_only=True
    )

    class Meta:
        model = MealRecordItem
        fields = ("meal_item", "meal_item_id", "quantity", "unit")


class MealRecordSerializer(serializers.ModelSerializer):
    """ 食事記録（ユーザーが登録） """
    meal_items = MealRecordItemSerializer(many=True)
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = MealRecord
        fields = ("id", "date", "time_of_day", "meal_items", "photo_url")

    def get_photo_url(self, obj):
        """ S3 の署名付きURLを返す(写真がある場合のみ) """
        if obj.photo:
            return generate_presigned_url(obj.photo.name)
        return None

    def create(self, validated_data):
        """ 食事記録を作成（ネストされた `meal_items` も保存） """
        meal_items_data = validated_data.pop("meal_items")
        meal_record = MealRecord.objects.create(**validated_data)

        for item_data in meal_items_data:
            MealRecordItem.objects.create(meal_record=meal_record, **item_data)

        return meal_record
