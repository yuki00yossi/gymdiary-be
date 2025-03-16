from rest_framework import serializers
from .models import TrainerProfile, TrainingPlan, TrainingApplication


class TrainingPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingPlan
        fields = "__all__"


class TrainerProfileSerializer(serializers.ModelSerializer):
    plans = TrainingPlanSerializer(many=True, read_only=True)

    class Meta:
        model = TrainerProfile
        fields = "__all__"


class TrainingApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingApplication
        fields = "__all__"
