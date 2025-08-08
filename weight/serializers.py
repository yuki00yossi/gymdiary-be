from rest_framework import serializers
from .models import WeightRecord


class NullableFloatField(serializers.FloatField):
    """
    空文字を None に変換する FloatField

    フォームから空文字が送信された場合に、None値に変換します。
    体脂肪率などのオプションフィールドで使用されます。
    """
    def to_internal_value(self, data):
        if data == "":
            return None
        return super().to_internal_value(data)


class WeightRecordSerializer(serializers.ModelSerializer):
    """
    体重記録シリアライザー

    体重記録の作成・更新・表示に使用されるシリアライザーです。

    Fields:
        id (int): 記録の一意識別子（読み取り専用）
        weight (float): 体重（kg）、必須
        fat (float): 体脂肪率（%）、オプション、空文字はNoneに変換
        record_date (datetime): 記録日時、必須
        created_at (datetime): 作成日時（読み取り専用）
        updated_at (datetime): 更新日時（読み取り専用）

    Example:
        {
            "weight": 70.5,
            "fat": 15.2,
            "record_date": "2024-01-15T10:30:00Z"
        }
    """
    fat = NullableFloatField(
        required=False,
        allow_null=True,
        default=None,
        help_text='体脂肪率（%）、オプション'
    )

    class Meta:
        model = WeightRecord
        fields = (
            'id', 'weight', 'fat', 'record_date',
            'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')
