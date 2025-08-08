from rest_framework import serializers
from .models import MySet, MySetExercise, MySetExerciseSet


class MySetExerciseSetSerializer(serializers.ModelSerializer):
    """
    マイセット種目のセットシリアライザー

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
        model = MySetExerciseSet
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


class MySetExerciseSerializer(serializers.ModelSerializer):
    """
    マイセット種目シリアライザー

    Fields:
        exercise (int): エクササイズID
        exercise_name (str): エクササイズ名（読み取り専用）
        exercise_type (str): エクササイズタイプ（読み取り専用）
        order (int): 種目の順番
        sets (list): セット情報のリスト
    """
    sets = MySetExerciseSetSerializer(many=True)
    exercise_name = serializers.SerializerMethodField()
    exercise_type = serializers.SerializerMethodField()

    class Meta:
        model = MySetExercise
        fields = ('exercise', 'exercise_name', 'exercise_type', 'order', 'sets')

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


class MySetSerializer(serializers.ModelSerializer):
    """
    マイセットシリアライザー

    マイセットとネストされた種目、セット情報を一括で管理します。

    Fields:
        id (int): マイセットの一意識別子（読み取り専用）
        name (str): セット名、必須
        description (str): 説明、オプション
        exercises (list): 種目情報のリスト
        created_at (datetime): 作成日時（読み取り専用）
        updated_at (datetime): 更新日時（読み取り専用）
    """
    exercises = MySetExerciseSerializer(many=True)

    class Meta:
        model = MySet
        fields = ('id', 'name', 'description', 'exercises', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("セット名を入力してください。")
        return value.strip()

    def validate_exercises(self, value):
        if not value:
            raise serializers.ValidationError("少なくとも1つの種目を含めてください。")

        # 種目の順番が重複していないかチェック
        orders = [exercise.get('order') for exercise in value]
        if len(orders) != len(set(orders)):
            raise serializers.ValidationError("種目の順番が重複しています。")

        # 各種目でセットの順番が重複していないかチェック
        for exercise in value:
            sets = exercise.get('sets', [])
            if sets:
                set_orders = [s.get('order') for s in sets]
                if len(set_orders) != len(set(set_orders)):
                    exercise_name = exercise.get('exercise').name if exercise.get('exercise') else "不明な種目"
                    raise serializers.ValidationError(f"種目「{exercise_name}」でセットの順番が重複しています。")

        return value

    def create(self, validated_data):
        """マイセットを作成（ネストされた種目とセットも保存）"""
        request = self.context.get("request")
        exercises_data = validated_data.pop('exercises')

        # MySetを作成
        myset = MySet.objects.create(
            user_id=request.user,
            **validated_data
        )

        # ネストされた種目とセットを作成
        self._create_exercises(myset, exercises_data)

        return myset

    def update(self, instance, validated_data):
        """マイセットを更新（ネストされた種目とセットも更新）"""
        exercises_data = validated_data.pop('exercises', None)

        # MySetの基本情報を更新
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.save()

        if exercises_data is not None:
            # 既存の種目とセットを削除してから新しく作成（デリートインサート）
            instance.exercises.all().delete()
            self._create_exercises(instance, exercises_data)

        return instance

    def _create_exercises(self, myset, exercises_data):
        """種目とセットを作成"""
        for exercise_data in exercises_data:
            sets_data = exercise_data.pop('sets')

            # MySetExerciseを作成
            exercise = MySetExercise.objects.create(
                myset_id=myset,
                **exercise_data
            )

            # MySetExerciseSetを作成
            for set_data in sets_data:
                MySetExerciseSet.objects.create(
                    myset_exercise_id=exercise,
                    **set_data
                )

