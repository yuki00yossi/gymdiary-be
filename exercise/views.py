from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q, Case, When, IntegerField
from collections import defaultdict
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import ExerciseCategory, Exercise
from .serializers import ExerciseCategorySerializer, ExerciseSerializer, ExerciseListSerializer


@extend_schema_view(
    list=extend_schema(
        summary="エクササイズ部位別一覧取得",
        description="エクササイズを部位別にグループ化して取得します。よく使うエクササイズは履歴に基づいてソートされ、ユーザーが作成したエクササイズが上位に表示されます。",
        tags=["エクササイズ"]
    ),
    create=extend_schema(
        summary="エクササイズ作成",
        description="新しいカスタムエクササイズを作成します。",
        tags=["エクササイズ"]
    ),
    retrieve=extend_schema(
        summary="エクササイズ詳細取得",
        description="指定したIDのエクササイズの詳細を取得します。",
        tags=["エクササイズ"]
    ),
    update=extend_schema(
        summary="エクササイズ更新",
        description="指定したIDのエクササイズを更新します。公式エクササイズは更新できません。",
        tags=["エクササイズ"]
    ),
    partial_update=extend_schema(
        summary="エクササイズ部分更新",
        description="指定したIDのエクササイズを部分的に更新します。",
        tags=["エクササイズ"]
    ),
    destroy=extend_schema(
        summary="エクササイズ削除",
        description="指定したIDのエクササイズを削除します。公式エクササイズは削除できません。",
        tags=["エクササイズ"]
    ),
)
class ExerciseViewSet(viewsets.ModelViewSet):
    """
    エクササイズ API（統合版）

    公式エクササイズとユーザーカスタムエクササイズを統合して管理します。
    よく使うエクササイズは、ユーザーのトレーニング履歴を基にソートされます。
    """
    serializer_class = ExerciseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        ログインユーザーがアクセス可能なエクササイズを取得
        （公式エクササイズ + ユーザーが作成したエクササイズ）
        """
        return Exercise.objects.filter(
            Q(is_official=True) | Q(created_by=self.request.user)
        ).select_related('category', 'created_by').order_by(
            # ユーザー作成分を上位に表示
            Case(
                When(is_official=True, then=1),
                When(is_official=False, then=0),
                output_field=IntegerField()
            ),
            'category__name',
            'name'
        )

    def list(self, request, *args, **kwargs):
        """エクササイズを部位別にグループ化して返す"""
        # カテゴリ別にエクササイズを取得
        categories = ExerciseCategory.objects.prefetch_related(
            'exercises'
        ).all()

        # ユーザーのエクササイズ使用頻度を計算
        exercise_usage = self._get_user_exercise_usage(request.user)

        result = {}

        # よく使うエクササイズを先に作成
        frequent_exercises = self._get_frequent_exercises(request.user, exercise_usage)
        print(frequent_exercises)
        if frequent_exercises:
            result['よく使う'] = frequent_exercises

        # 部位別エクササイズを作成
        for category in categories:
            exercises = []

            # ユーザーがアクセス可能なエクササイズを取得（ユーザー作成分を上位に）
            category_exercises = Exercise.objects.filter(
                category=category
            ).filter(
                Q(is_official=True) | Q(created_by=request.user)
            ).order_by(
                Case(
                    When(is_official=True, then=1),
                    When(is_official=False, then=0),
                    output_field=IntegerField()
                ),
                'name'
            )

            for exercise in category_exercises:
                exercises.append({
                    'id': exercise.id,
                    'name': exercise.name,
                    'description': exercise.description,
                    'type': exercise.exercise_type
                })

            if exercises:
                result[category.name] = exercises

        print(result)
        return Response(result)

    def create(self, request, *args, **kwargs):
        """エクササイズを作成"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 同じカテゴリで同じ名前のエクササイズがないかチェック
        if Exercise.objects.filter(
            created_by=request.user,
            name=serializer.validated_data['name'],
            category=serializer.validated_data['category']
        ).exists():
            return Response(
                {"non_field_errors": ["同じカテゴリに同じ名前のエクササイズが既に存在します。"]},
                status=status.HTTP_400_BAD_REQUEST
            )

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def update(self, request, *args, **kwargs):
        """エクササイズを更新"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        # 公式エクササイズは更新不可
        if instance.is_official:
            return Response(
                {"detail": "公式エクササイズは更新できません。"},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        # 名前やカテゴリが変更される場合、重複チェック
        new_name = serializer.validated_data.get('name')
        new_category = serializer.validated_data.get('category')
        if ((new_name and new_name != instance.name) or
            (new_category and new_category != instance.category)):
            if Exercise.objects.filter(
                created_by=request.user,
                name=new_name or instance.name,
                category=new_category or instance.category
            ).exclude(id=instance.id).exists():
                return Response(
                    {"non_field_errors": ["同じカテゴリに同じ名前のエクササイズが既に存在します。"]},
                    status=status.HTTP_400_BAD_REQUEST
                )

        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """エクササイズを削除"""
        instance = self.get_object()

        # 公式エクササイズは削除不可
        if instance.is_official:
            return Response(
                {"detail": "公式エクササイズは削除できません。"},
                status=status.HTTP_403_FORBIDDEN
            )

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_object(self):
        """
        オブジェクトを取得（ユーザーのアクセス権限をチェック）
        公式エクササイズまたはユーザーが作成したエクササイズのみアクセス可能
        """
        obj = super().get_object()
        if not obj.is_official and obj.created_by != self.request.user:
            self.permission_denied(
                self.request,
                message="このエクササイズにはアクセスできません。"
            )
        return obj

    def _get_user_exercise_usage(self, user):
        """ユーザーのエクササイズ使用頻度を取得"""
        from workout.models import WorkoutExercise

        usage = defaultdict(int)

        # 統合されたExerciseモデルでの使用頻度を計算
        workout_exercises = WorkoutExercise.objects.filter(
            workout_session_id__user_id=user
        ).select_related('exercise')

        for workout_exercise in workout_exercises:
            usage[workout_exercise.exercise.id] += 1

        return usage

    def _get_frequent_exercises(self, user, exercise_usage, limit=4):
        """よく使うエクササイズを取得"""
        if not exercise_usage:
            return []

        # 使用頻度順にソート
        sorted_exercises = sorted(exercise_usage.items(), key=lambda x: x[1], reverse=True)[:limit]

        frequent_exercises = []
        for exercise_id, usage_count in sorted_exercises:
            try:
                exercise = Exercise.objects.get(
                    id=exercise_id,
                    **({'is_official': True} if Exercise.objects.get(id=exercise_id).is_official
                       else {'created_by': user})
                )
                frequent_exercises.append({
                    'id': exercise.id,
                    'name': exercise.name,
                    'description': exercise.description,
                    'type': exercise.exercise_type
                })
            except Exercise.DoesNotExist:
                continue

        return frequent_exercises


@extend_schema_view(
    list=extend_schema(
        summary="エクササイズカテゴリ一覧取得",
        description="エクササイズのカテゴリ一覧を取得します。",
        tags=["エクササイズカテゴリ"]
    ),
)
class ExerciseCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """エクササイズカテゴリ取得 API"""
    queryset = ExerciseCategory.objects.all()
    serializer_class = ExerciseCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
