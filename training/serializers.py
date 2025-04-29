from rest_framework import serializers
from .models import TrainingSession, Workout, WorkoutSet, MySet, MyWorkout, MyWorkoutSet, MySetSession, MySetWorkoutRecord, MySetWorkoutSetRecord

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


class MyWorkoutSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyWorkoutSet
        fields = ['id', 'weight', 'reps', 'distance', 'time', 'memo']


class MyWorkoutSerializer(serializers.ModelSerializer):
    sets = MyWorkoutSetSerializer(many=True)

    class Meta:
        model = MyWorkout
        fields = ['id', 'menu', 'type', 'unit', 'memo', 'sets']


class MySetSerializer(serializers.ModelSerializer):
    workouts = MyWorkoutSerializer(many=True)
    created_by = serializers.SerializerMethodField()

    class Meta:
        model = MySet
        fields = ['id', 'name', 'created_by', 'created_at', 'updated_at', 'workouts']

    def get_created_by(self, obj):
        return {
            "id": obj.created_by.id,
            "username": obj.created_by.username
        }

    def create(self, validated_data):
        workouts_data = validated_data.pop('workouts')
        myset = MySet.objects.create(**validated_data)
        for workout_data in workouts_data:
            sets_data = workout_data.pop('sets')
            workout = MyWorkout.objects.create(myset=myset, **workout_data)
            for set_data in sets_data:
                MyWorkoutSet.objects.create(workout=workout, **set_data)
        return myset

    def update(self, instance, validated_data):
        workouts_data = validated_data.pop('workouts', None)
        instance.name = validated_data.get('name', instance.name)
        instance.save()

        if workouts_data is not None:
            # 既存のワークアウトとセットを全部削除して、作り直し
            instance.workouts.all().delete()
            for workout_data in workouts_data:
                sets_data = workout_data.pop('sets')
                workout = MyWorkout.objects.create(myset=instance, **workout_data)
                for set_data in sets_data:
                    MyWorkoutSet.objects.create(workout=workout, **set_data)

        return instance


class MySetWorkoutSetRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = MySetWorkoutSetRecord
        fields = ['weight', 'reps', 'distance', 'time', 'memo']


class MySetWorkoutRecordSerializer(serializers.ModelSerializer):
    sets = MySetWorkoutSetRecordSerializer(many=True)

    class Meta:
        model = MySetWorkoutRecord
        fields = ['menu', 'type', 'unit', 'memo', 'sets']


class MySetSessionCreateSerializer(serializers.Serializer):
    date = serializers.DateField()
    workouts = MySetWorkoutRecordSerializer(many=True)


# --- セット記録 ---
class MySetWorkoutSetRecordDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = MySetWorkoutSetRecord
        fields = ['id', 'weight', 'reps', 'distance', 'time', 'memo']


# --- ワークアウト記録 ---
class MySetWorkoutRecordDetailSerializer(serializers.ModelSerializer):
    sets = MySetWorkoutSetRecordDetailSerializer(many=True)

    class Meta:
        model = MySetWorkoutRecord
        fields = ['id', 'menu', 'type', 'unit', 'memo', 'sets']


# --- 記録詳細用 ---
class MySetSessionDetailSerializer(serializers.ModelSerializer):
    myset_name = serializers.CharField(source='myset.name')
    workouts = MySetWorkoutRecordDetailSerializer(many=True)

    class Meta:
        model = MySetSession
        fields = ['id', 'date', 'myset_name', 'workouts']


# --- 記録一覧用 ---
class MySetSessionListSerializer(serializers.ModelSerializer):
    myset_name = serializers.CharField(source='myset.name')

    class Meta:
        model = MySetSession
        fields = ['id', 'date', 'myset_name', 'created_at']
