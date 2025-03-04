from rest_framework import serializers
from .models import TrainingSession, Workout, WorkoutSet

from django.utils.timezone import make_aware
from datetime import datetime


class WorkoutSetSerializer(serializers.ModelSerializer):
    """ セットのシリアライザー """
    weight = serializers.FloatField(required=False, allow_null=True)
    reps = serializers.IntegerField(required=False, allow_null=True)
    distance = serializers.FloatField(required=False, allow_null=True)
    time = serializers.FloatField(required=False, allow_null=True)

    class Meta:
        """ メタ情報 """
        model = WorkoutSet
        fields = ("weight", "reps", "distance", "time", "memo")


class WorkoutSerializer(serializers.ModelSerializer):
    """ ワークアウト（種目ごとの記録）のシリアライザー """
    sets = WorkoutSetSerializer(many=True)

    class Meta:
        """ メタ情報 """
        model = Workout
        fields = ("menu", "type", "unit", "memo", "sets")


class TrainingSessionSerializer(serializers.ModelSerializer):
    """ トレーニングセッションのシリアライザー """
    workouts = WorkoutSerializer(many=True)

    class Meta:
        """ メタ情報 """
        model = TrainingSession
        fields = ("id", "date", "workouts", "created_at")

    def create(self, validated_data):
        """ ネストされたワークアウトとセットを個別に保存する """
        request_user = self.context['request'].user
        workouts_data = validated_data.pop("workouts")  # ネストされたワークアウトを取得

        date = validated_data.get('date')
        if isinstance(date, str):
            date = make_aware(datetime.strptime(date, "%Y-%m-%d"))

        session, created = TrainingSession.objects.update_or_create(
            date=date, user=request_user,
            defaults=validated_data
        )

        session.workouts.all().delete()

        for workout_data in workouts_data:
            sets_data = workout_data.pop("sets")  # ネストされたセットを取得
            workout = Workout.objects.create(session=session, **workout_data)  # ワークアウトを作成

            for set_data in sets_data:
                WorkoutSet.objects.create(workout=workout, **set_data)  # セットを作成

        return session
