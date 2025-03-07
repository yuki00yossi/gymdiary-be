from rest_framework import serializers
from .models import WeightRecord


class NullableFloatField(serializers.FloatField):
    """ 空文字を None に変換する FloatField """
    def to_internal_value(self, data):
        if data == "":
            return None
        return super().to_internal_value(data)



class WeightRecordSerializer(serializers.ModelSerializer):
    """ 体重記録シリアライザー """
    fat = NullableFloatField(required=False, allow_null=True, default=None)

    class Meta:
        model = WeightRecord
        fields = (
            'id', 'weight', 'fat', 'record_date',
            'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')
