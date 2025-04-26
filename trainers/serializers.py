from rest_framework import serializers
from .models import TrainerProfile


# class TrainingPlanSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TrainingPlan
#         fields = "__all__"


class TrainerProfileSerializer(serializers.ModelSerializer):
    """ トレーナープロフィールシリアライザ """
    class Meta:
        model = TrainerProfile
        fields = ['user', 'bio', 'specialties', 'certifications', 'career', 'intro_video_url']
        read_only_fields = ['user']
        extra_kwargs = {
            'certifications': {'required': False},
            'intro_video_url': {'required': False},
        }

    def validate_specialties(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("リスト形式で送信してください")
        return value

    def validate_certifications(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("リスト形式で送信してください")
        return value


# class TrainingApplicationSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TrainingApplication
#         fields = "__all__"
