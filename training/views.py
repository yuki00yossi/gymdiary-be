from rest_framework import generics, permissions, viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .models import (TrainingSession, MySet, MySetSession,
                     MySetWorkoutRecord, MySetWorkoutSetRecord)
from .serializers import (
    TrainingSessionSerializer, MySetSerializer,
    MySetSessionCreateSerializer,
    MySetSessionListSerializer,
    MySetSessionDetailSerializer)

from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes


# Create your views here.
@extend_schema_view(
    get=extend_schema(
        summary="トレーニング記録一覧取得",
        description="ログインユーザーのトレーニング記録一覧を取得します。",
        tags=["トレーニング記録"]
    ),
    post=extend_schema(
        summary="トレーニング記録作成",
        description="新しいトレーニング記録を作成します。ユーザーは自動的に紐づけられます。",
        tags=["トレーニング記録"]
    )
)
class TrainingSessionListCreateView(generics.ListCreateAPIView):
    """
    トレーニング記録の取得・作成API

    ユーザーのトレーニング記録を一覧取得・作成するためのAPIです。
    認証が必要で、ログインユーザーのトレーニング記録のみを操作できます。
    """
    serializer_class = TrainingSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """自分のトレーニング記録のみ取得"""
        return TrainingSession.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """トレーニング記録を作成(ログインユーザーに紐づけ)"""
        serializer.save(user=self.request.user)


@extend_schema_view(
    get=extend_schema(
        summary="トレーニング記録詳細取得",
        description="指定したIDのトレーニング記録の詳細を取得します。",
        tags=["トレーニング記録"]
    ),
    delete=extend_schema(
        summary="トレーニング記録削除",
        description="指定したIDのトレーニング記録を削除します。",
        tags=["トレーニング記録"]
    )
)
class TrainingSessionDetailView(generics.RetrieveDestroyAPIView):
    """
    トレーニング記録詳細・削除API

    指定したトレーニング記録の詳細取得および削除を行います。
    """
    serializer_class = TrainingSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TrainingSession.objects.filter(user=self.request.user)


@extend_schema_view(
    list=extend_schema(
        summary="マイセット一覧取得",
        description="ログインユーザーのマイセット一覧を取得します。",
        tags=["マイセット"]
    ),
    create=extend_schema(
        summary="マイセット作成",
        description="新しいマイセットを作成します。作成者とユーザーは自動的に紐づけられます。",
        tags=["マイセット"]
    ),
    retrieve=extend_schema(
        summary="マイセット詳細取得",
        description="指定したIDのマイセットの詳細を取得します。",
        tags=["マイセット"]
    ),
    update=extend_schema(
        summary="マイセット更新",
        description="指定したIDのマイセットを更新します。",
        tags=["マイセット"]
    ),
    partial_update=extend_schema(
        summary="マイセット部分更新",
        description="指定したIDのマイセットを部分的に更新します。",
        tags=["マイセット"]
    ),
    destroy=extend_schema(
        summary="マイセット削除",
        description="指定したIDのマイセットを削除します。削除権限チェックが行われます。",
        responses={
            200: {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "削除完了メッセージ"}
                },
                "example": {"message": "マイセットを削除しました！"}
            },
            403: {
                "type": "object",
                "properties": {
                    "detail": {"type": "string", "description": "エラーメッセージ"}
                },
                "example": {"detail": "あなたには削除権限がありません。"}
            }
        },
        tags=["マイセット"]
    )
)
class MySetViewSet(viewsets.ModelViewSet):
    """
    マイセット管理API

    トレーニングのマイセット（メニューセット）を管理するAPIです。
    ユーザーごとに個別のマイセットを作成・管理できます。
    """
    queryset = MySet.objects.all()
    serializer_class = MySetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # 自分が持ってるマイセットだけ（作成者関係なく、自分に紐づくもの）
        return MySet.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,  # このマイセットを使うのは自分
            created_by=self.request.user  # 作成者も自分（トレーナー提供の場合はあとで切り替え）
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            return Response({"detail": "あなたには削除権限がありません。"}, status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return Response({"message": "マイセットを削除しました！"}, status=status.HTTP_200_OK)


class MySetRecordView(APIView):
    """
    マイセット記録管理API

    マイセットに基づくトレーニング記録の取得・作成を行います。
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="マイセット最新記録取得",
        description="指定したマイセットの最新のトレーニング記録を取得します。",
        parameters=[
            OpenApiParameter(
                name='myset_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='マイセットID'
            ),
        ],
        responses={
            200: MySetSessionDetailSerializer,
            404: {
                "type": "object",
                "properties": {
                    "detail": {"type": "string", "description": "エラーメッセージ"}
                },
                "examples": {
                    "myset_not_found": {
                        "summary": "マイセットが見つからない",
                        "value": {"detail": "マイセットが見つかりません"}
                    },
                    "record_not_found": {
                        "summary": "記録が存在しない",
                        "value": {"detail": "記録が存在しません"}
                    }
                }
            }
        },
        tags=["マイセット記録"]
    )
    def get(self, request, myset_id):
        """マイセットの最新記録を取得"""
        try:
            myset = MySet.objects.get(id=myset_id, user=request.user)
        except MySet.DoesNotExist:
            return Response({"detail": "マイセットが見つかりません"}, status=status.HTTP_404_NOT_FOUND)

        latest_session = MySetSession.objects.filter(myset=myset).order_by("-date", "-created_at").first()

        if not latest_session:
            return Response({"detail": "記録が存在しません"}, status=status.HTTP_404_NOT_FOUND)

        serializer = MySetSessionDetailSerializer(latest_session)
        return Response(serializer.data)

    @extend_schema(
        summary="マイセット記録作成",
        description="指定したマイセットに基づいて新しいトレーニング記録を作成します。",
        parameters=[
            OpenApiParameter(
                name='myset_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='マイセットID'
            ),
        ],
        request=MySetSessionCreateSerializer,
        responses={
            201: {
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "description": "作成されたセッションID"},
                    "message": {"type": "string", "description": "成功メッセージ"}
                },
                "example": {
                    "id": 123,
                    "message": "マイセットから記録を作成しました！"
                }
            },
            404: {
                "type": "object",
                "properties": {
                    "detail": {"type": "string", "description": "エラーメッセージ"}
                },
                "example": {"detail": "対象のマイセットが見つかりません。"}
            }
        },
        tags=["マイセット記録"]
    )
    def post(self, request, myset_id):
        """マイセットから記録を作成"""
        try:
            myset = MySet.objects.get(id=myset_id, user=request.user)
        except MySet.DoesNotExist:
            return Response({"detail": "対象のマイセットが見つかりません。"}, status=status.HTTP_404_NOT_FOUND)

        serializer = MySetSessionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # セッション作成
        session = MySetSession.objects.create(
            user=request.user,
            myset=myset,
            date=serializer.validated_data['date']
        )

        # ワークアウトとセット作成
        for workout_data in serializer.validated_data['workouts']:
            if len(workout_data.get('sets')) == 0:
                continue
            workout = MySetWorkoutRecord.objects.create(
                session=session,
                menu=workout_data['menu'],
                type=workout_data['type'],
                unit=workout_data['unit'],
                memo=workout_data.get('memo', "")
            )
            for set_data in workout_data['sets']:
                MySetWorkoutSetRecord.objects.create(
                    workout=workout,
                    weight=set_data.get('weight'),
                    reps=set_data.get('reps'),
                    distance=set_data.get('distance'),
                    time=set_data.get('time'),
                    memo=set_data.get('memo', "")
                )

        return Response({"id": session.id, "message": "マイセットから記録を作成しました！"}, status=status.HTTP_201_CREATED)


@extend_schema(
    summary="マイセット記録一覧取得",
    description="ログインユーザーのマイセット記録一覧を日付の降順で取得します。",
    tags=["マイセット記録"]
)
class MySetSessionListView(generics.ListAPIView):
    """
    マイセット記録一覧取得API

    ユーザーのマイセット記録の一覧を取得します。
    """
    serializer_class = MySetSessionListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MySetSession.objects.filter(user=self.request.user).order_by('-date')


@extend_schema(
    summary="マイセット記録詳細取得",
    description="指定したIDのマイセット記録の詳細を取得します。",
    tags=["マイセット記録"]
)
class MySetSessionDetailView(generics.RetrieveAPIView):
    """
    マイセット記録詳細取得API

    指定したマイセット記録の詳細情報を取得します。
    """
    serializer_class = MySetSessionDetailSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return MySetSession.objects.filter(user=self.request.user)
