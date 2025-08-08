from rest_framework import serializers
from .models import WorkoutSession, WorkoutExercise, WorkoutExerciseSet


class WorkoutExerciseSetSerializer(serializers.ModelSerializer):
    """
    トレーニング種目のセットシリアライザー

    Fields:
        order (int): セットの順番
        weight (float): 重量(kg)、オプション
        reps (int): 回数、オプション
        distance (float): 距離、オプション
        distance_unit (str): 距離単位、オプション
        duration (int): 時間、オプション
        duration_unit (str): 時間単位、オプション
        fat_burn (float): 脂肪燃焼(kcal)、オプション
        memo (str): メモ、オプション
    """

    class Meta:
        model = WorkoutExerciseSet
        fields = (
            'order', 'weight', 'reps', 'distance', 'distance_unit',
            'duration', 'duration_unit', 'fat_burn', 'memo'
        )

    def validate_order(self, value):
        if value < 1:
            raise serializers.ValidationError("順番は1以上にしてください。")
        return value

    def validate_weight(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("重量は0以上にしてください。")
        return value

    def validate_reps(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("回数は0以上にしてください。")
        return value

    def validate_distance(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("距離は0以上にしてください。")
        return value

    def validate_duration(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("時間は0以上にしてください。")
        return value

    def validate_fat_burn(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("脂肪燃焼は0以上にしてください。")
        return value


class WorkoutExerciseSerializer(serializers.ModelSerializer):
    """
    トレーニング種目シリアライザー

    Fields:
        exercise (int): エクササイズID
        exercise_name (str): エクササイズ名（読み取り専用）
        exercise_type (str): エクササイズタイプ（読み取り専用）
        order (int): 種目の順番
        workout_exercise_sets (list): セット情報のリスト
    """
    workout_exercise_sets = WorkoutExerciseSetSerializer(many=True)
    exercise_name = serializers.SerializerMethodField()
    exercise_type = serializers.SerializerMethodField()

    class Meta:
        model = WorkoutExercise
        fields = ('exercise', 'exercise_name', 'exercise_type', 'order', 'workout_exercise_sets')

    def validate_order(self, value):
        if value < 1:
            raise serializers.ValidationError("順番は1以上にしてください。")
        return value

    def get_exercise_name(self, obj):
        """エクササイズ名を取得（Null対応）"""
        return obj.exercise.name if obj.exercise else "（未設定）"

    def get_exercise_type(self, obj):
        """エクササイズタイプを取得（Null対応）"""
        return obj.exercise.exercise_type if obj.exercise else "unknown"

    def validate_exercise(self, value):
        """エクササイズのアクセス権限をチェック"""
        if value is None:
            raise serializers.ValidationError("エクササイズを指定してください。")

        request = self.context.get('request')
        if request:
            # 公式エクササイズまたはユーザーが作成したエクササイズのみ使用可能
            if not value.is_official and value.created_by != request.user:
                raise serializers.ValidationError("このエクササイズを使用する権限がありません。")
        return value


class WorkoutSessionSerializer(serializers.ModelSerializer):
    """
    トレーニングセッションシリアライザー

    トレーニングセッションとネストされた種目、セット情報を一括で管理します。

    Fields:
        id (int): トレーニングセッションの一意識別子（読み取り専用）
        name (str): セッション名、必須
        date (date): トレーニング日、必須
        memo (str): メモ、オプション
        workout_exercises (list): 種目情報のリスト
        created_at (datetime): 作成日時（読み取り専用）
        updated_at (datetime): 更新日時（読み取り専用）
    """
    workout_exercises = WorkoutExerciseSerializer(many=True)

    class Meta:
        model = WorkoutSession
        fields = ('id', 'name', 'date', 'memo', 'workout_exercises', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("セッション名を入力してください。")
        return value.strip()

    def validate_workout_exercises(self, value):
        if not value:
            raise serializers.ValidationError("少なくとも1つの種目を含めてください。")

        # 種目の順番が重複していないかチェック
        orders = [exercise.get('order') for exercise in value]
        if len(orders) != len(set(orders)):
            raise serializers.ValidationError("種目の順番が重複しています。")

        # 各種目でセットの順番が重複していないかチェック
        for exercise in value:
            sets = exercise.get('workout_exercise_sets', [])
            if sets:
                set_orders = [s.get('order') for s in sets]
                if len(set_orders) != len(set(set_orders)):
                    exercise_name = exercise.get('exercise').name if exercise.get('exercise') else "不明な種目"
                    raise serializers.ValidationError(f"種目「{exercise_name}」でセットの順番が重複しています。")

        return value

    def create(self, validated_data):
        """トレーニングセッションを作成（ネストされた種目とセットも保存）"""
        request = self.context.get("request")
        exercises_data = validated_data.pop('workout_exercises')

        # WorkoutSessionを作成
        workout_session = WorkoutSession.objects.create(
            user_id=request.user,
            **validated_data
        )

        # ネストされた種目とセットを作成
        self._create_exercises(workout_session, exercises_data)

        return workout_session

    def update(self, instance, validated_data):
        """トレーニングセッションを更新（ネストされた種目とセットも更新）"""
        exercises_data = validated_data.pop('workout_exercises', None)

        # WorkoutSessionの基本情報を更新
        instance.name = validated_data.get('name', instance.name)
        instance.date = validated_data.get('date', instance.date)
        instance.memo = validated_data.get('memo', instance.memo)
        instance.save()

        if exercises_data is not None:
            # 既存の種目とセットを削除してから新しく作成（デリートインサート）
            instance.workout_exercises.all().delete()
            self._create_exercises(instance, exercises_data)

        return instance

    def _create_exercises(self, workout_session, exercises_data):
        """種目とセットを作成"""
        for exercise_data in exercises_data:
            sets_data = exercise_data.pop('workout_exercise_sets')

            # WorkoutExerciseを作成
            exercise = WorkoutExercise.objects.create(
                workout_session_id=workout_session,
                **exercise_data
            )

            # WorkoutExerciseSetを作成
            for set_data in sets_data:
                WorkoutExerciseSet.objects.create(
                    workout_exercise_id=exercise,
                    **set_data
                )