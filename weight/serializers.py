from rest_framework import serializers
from .models import WeightRecord


class WeightRecordSerializer(serializers.ModelSerializer):
    """ 体重記録シリアライザー """
    class Meta:
        model = WeightRecord
        fields = (
            'id', 'weight', 'fat', 'record_date',
            'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')
