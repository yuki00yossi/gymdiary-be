from rest_framework import serializers
from .models import TrainingSession, Workout, WorkoutSet


class WorkoutSetSerializer(serializers.ModelSerializer):
    """ セットのシリアライザー """
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
        workouts_data = validated_data.pop("workouts")  # ネストされたワークアウトを取得
        session = TrainingSession.objects.create(**validated_data)  # まずセッションを作成

        for workout_data in workouts_data:
            sets_data = workout_data.pop("sets")  # ネストされたセットを取得
            workout = Workout.objects.create(session=session, **workout_data)  # ワークアウトを作成

            for set_data in sets_data:
                WorkoutSet.objects.create(workout=workout, **set_data)  # セットを作成

        return session
