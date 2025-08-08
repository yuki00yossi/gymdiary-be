from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Prefetch
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import WorkoutSession, WorkoutExercise, WorkoutExerciseSet
from .serializers import WorkoutSessionSerializer


@extend_schema_view(
    list=extend_schema(
        summary="トレーニングセッション一覧取得",
        description="ログインユーザーのトレーニングセッション一覧を取得します。日付でフィルタリングも可能です。",
        parameters=[
            OpenApiParameter(
                name='date',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='取得したい日付（YYYY-MM-DD形式）',
            ),
            OpenApiParameter(
                name='date_from',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='開始日（YYYY-MM-DD形式）',
            ),
            OpenApiParameter(
                name='date_to',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='終了日（YYYY-MM-DD形式）',
            ),
        ],
        tags=["トレーニング記録"]
    ),
    create=extend_schema(
        summary="トレーニングセッション作成",
        description="新しいトレーニングセッションを作成します。種目とセット情報も一括で作成できます。",
        tags=["トレーニング記録"]
    ),
    retrieve=extend_schema(
        summary="トレーニングセッション詳細取得",
        description="指定したIDのトレーニングセッションの詳細を取得します。",
        tags=["トレーニング記録"]
    ),
    update=extend_schema(
        summary="トレーニングセッション更新",
        description="指定したIDのトレーニングセッションを更新します。種目とセット情報も一括で更新できます。",
        tags=["トレーニング記録"]
    ),
    partial_update=extend_schema(
        summary="トレーニングセッション部分更新",
        description="指定したIDのトレーニングセッションを部分的に更新します。",
        tags=["トレーニング記録"]
    ),
    destroy=extend_schema(
        summary="トレーニングセッション削除",
        description="指定したIDのトレーニングセッションを削除します。関連する種目とセット情報も削除されます。",
        tags=["トレーニング記録"]
    ),
)
class WorkoutSessionViewSet(viewsets.ModelViewSet):
    """
    トレーニングセッションのCRUD API

    トレーニングセッションの作成、取得、更新、削除を行います。
    すべての操作はログインユーザーのデータのみを対象とします。
    """
    serializer_class = WorkoutSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """ログインユーザーのトレーニングセッションのみ取得（関連データも含む）"""
        queryset = WorkoutSession.objects.filter(
            user_id=self.request.user
        ).prefetch_related(
            Prefetch(
                'workout_exercises',
                queryset=WorkoutExercise.objects.order_by('order').prefetch_related(
                    Prefetch(
                        'workout_exercise_sets',
                        queryset=WorkoutExerciseSet.objects.order_by('order')
                    )
                )
            )
        ).order_by('-date', '-created_at')

        # クエリパラメータでフィルタリング
        date = self.request.query_params.get('date')
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')

        if date:
            queryset = queryset.filter(date=date)
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)

        return queryset

    def create(self, request, *args, **kwargs):
        """トレーニングセッションを作成"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def update(self, request, *args, **kwargs):
        """トレーニングセッションを更新"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        # 名前や日付が変更される場合、同じ日に同じ名前のセッションが他に存在しないかチェック
        new_name = serializer.validated_data.get('name')
        new_date = serializer.validated_data.get('date')
        if (new_name and new_name != instance.name) or (new_date and new_date != instance.date):
            if WorkoutSession.objects.filter(
                user_id=request.user,
                name=new_name or instance.name,
                date=new_date or instance.date
            ).exclude(id=instance.id).exists():
                return Response(
                    {"non_field_errors": ["同じ日に同じ名前のトレーニングセッションが既に存在します。"]},
                    status=status.HTTP_400_BAD_REQUEST
                )

        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # prefetchされたキャッシュをクリア
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """トレーニングセッションを削除"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_object(self):
        """
        オブジェクトを取得（ユーザーのアクセス権限をチェック）
        ログインユーザーのトレーニングセッションのみアクセス可能
        """
        obj = super().get_object()
        if obj.user_id != self.request.user:
            self.permission_denied(
                self.request,
                message="このトレーニングセッションにはアクセスできません。"
            )
        return obj
