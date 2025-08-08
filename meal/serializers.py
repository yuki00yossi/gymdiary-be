import json

from rest_framework import serializers
from accounts.utils import generate_presigned_url  # S3の署名付きURLを生成
from .models import MealItem, MealRecord, MealRecordItem


class MealItemSerializer(serializers.ModelSerializer):
    """
    食品データシリアライザー（ユーザーが追加可能）

    食品の基本情報と栄養素データを管理します。
    基本的な栄養素（カロリー、タンパク質、脂質、炭水化物）は必須で、
    その他の栄養素（ビタミン、ミネラルなど）はオプションです。

    Fields:
        id (int): 食品の一意識別子（読み取り専用）
        name (str): 食品名、必須
        calories (float): カロリー（kcal）、必須、0以上
        protein (float): タンパク質（g）、必須、0以上
        fat (float): 脂質（g）、必須、0以上
        carbs (float): 炭水化物（g）、必須、0以上
        unit (str): 単位（g, ml, 個, 杯, 枚, 本, カップ, 人前）、必須
        base_quantity (float): 基準量（デフォルト: 100）、必須
        jan_ean_code (str): JAN/EANコード（商品バーコード番号）、オプション
        vitamin_a (float): ビタミンA（μgRAE）、オプション
        vitamin_d (float): ビタミンD（μg）、オプション
        vitamin_e (float): ビタミンE（mg）、オプション
        vitamin_k (float): ビタミンK（μg）、オプション
        vitamin_b1 (float): ビタミンB1（mg）、オプション
        vitamin_b2 (float): ビタミンB2（mg）、オプション
        niacin (float): ナイアシン（mgNE）、オプション
        vitamin_b6 (float): ビタミンB6（mg）、オプション
        vitamin_b12 (float): ビタミンB12（μg）、オプション
        folic_acid (float): 葉酸（μg）、オプション
        pantothenic_acid (float): パントテン酸（mg）、オプション
        biotin (float): ビオチン（μg）、オプション
        vitamin_c (float): ビタミンC（mg）、オプション
        sodium (float): ナトリウム（g）、オプション
        potassium (float): カリウム（mg）、オプション
        calcium (float): カルシウム（mg）、オプション
        magnesium (float): マグネシウム（mg）、オプション
        phosphorus (float): リン（mg）、オプション
        iron (float): 鉄（mg）、オプション
        zinc (float): 亜鉛（mg）、オプション
        copper (float): 銅（mg）、オプション
        manganese (float): マンガン（mg）、オプション
        iodine (float): ヨウ素（μg）、オプション
        selenium (float): セレン（μg）、オプション
        chromium (float): クロム（μg）、オプション
        molybdenum (float): モリブデン（μg）、オプション
        cholesterol (float): コレステロール（mg）、オプション
        dietary_fiber (float): 食物繊維（g）、オプション
        salt_equivalent (float): 食塩相当量（g）、オプション
    """

    class Meta:
        model = MealItem
        fields = (
            "id", "name", "calories", "protein", "fat", "carbs", "unit", "base_quantity",
            "jan_ean_code", "vitamin_a", "vitamin_d", "vitamin_e", "vitamin_k", "vitamin_b1", "vitamin_b2",
            "niacin", "vitamin_b6", "vitamin_b12", "folic_acid", "pantothenic_acid",
            "biotin", "vitamin_c", "sodium", "potassium", "calcium", "magnesium",
            "phosphorus", "iron", "zinc", "copper", "manganese", "iodine", "selenium",
            "chromium", "molybdenum", "cholesterol", "dietary_fiber", "salt_equivalent"
        )
        read_only_fields = ('created_by', "is_official")

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
    # meal_items = serializers.ListSerializer(child=MealRecordItemSerializer(), write_only=True)

    class Meta:
        model = MealRecord
        fields = ("id", "date", "time_of_day", "meal_items", "photo_key", "photo_url")

    def to_internal_value(self, data):
        """ meal_itemsをJSONパースして適切なフォーマットに変換 """
        mutable_data = data.copy()

        if "meal_items" in mutable_data and isinstance(mutable_data["meal_items"], str):
            try:
                mutable_data["meal_items"] = json.loads(mutable_data["meal_items"])
            except json.JSONDecodeError:
                raise serializers.ValidationError({"meal_items": "不正なJSON形式です。"})
        return super().to_internal_value(mutable_data)

    def get_photo_url(self, obj):
        """ S3 の署名付きURLを返す(写真がある場合のみ) """
        if obj.photo_key:
            return generate_presigned_url(obj.photo_key)
        return None

    def create(self, validated_data):
        """ 食事記録を作成（ネストされた `meal_items` も保存） """
        request = self.context.get("request")

        # `request.data` から `meal_items` を取得し、手動でパース
        meal_items_data = request.data.get("meal_items")
        if isinstance(meal_items_data, str):  # JSON 文字列の場合はデコード
            meal_items_data = json.loads(meal_items_data)

        meal_record = MealRecord.objects.create(
            user=request.user,
            date=validated_data["date"],
            time_of_day=validated_data["time_of_day"],
            photo_key=validated_data.get("photo_key"),
        )

        self._update_meal_items(meal_record, meal_items_data)
        return meal_record

    def update(self, instance, validated_data):
        """食事記録を更新(ネストされたmeal_itemsも更新)"""
        # `request.data` から `meal_items` を取得し、手動でパース
        request = self.context.get("request")
        meal_items_data = request.data.get("meal_items")
        if isinstance(meal_items_data, str):  # JSON 文字列の場合はデコード
            meal_items_data = json.loads(meal_items_data)

        # MealRecordの基本情報を更新
        instance.data = validated_data.get("date", instance.date)
        instance.time_of_day = validated_data.get("time_of_day", instance.time_of_day)
        instance.photo_key = validated_data.get("photo_key", instance.photo_key)
        instance.save()

        # meal_itemsを更新(デリートインサート)
        instance.meal_items.all().delete()
        self._update_meal_items(instance, meal_items_data)
        return instance

    def _update_meal_items(self, meal_record, meal_items_data):
        """meal_itemsを作成"""
        for item_data in meal_items_data:
            MealRecordItem.objects.create(
                meal_record=meal_record,
                meal_item_id=item_data["meal_item_id"],
                quantity=item_data["quantity"],
                unit=item_data["unit"]
            )
