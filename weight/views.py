from rest_framework import generics, permissions, status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from .models import WeightRecord
from .serializers import WeightRecordSerializer


# Create your views here.
@extend_schema_view(
    get=extend_schema(
        summary="体重記録一覧取得",
        description="ログインユーザーの体重記録一覧を取得します。",
        tags=["体重記録"]
    ),
    post=extend_schema(
        summary="体重記録作成・更新",
        description="新しい体重記録を作成します。同じ日付の記録が既に存在する場合は更新されます。",
        request=WeightRecordSerializer,
        responses={
            200: WeightRecordSerializer,
            201: WeightRecordSerializer,
            400: {
                "type": "object",
                "properties": {
                    "weight": {"type": "array", "items": {"type": "string"}},
                    "record_date": {"type": "array", "items": {"type": "string"}}
                },
                "example": {
                    "weight": ["この項目は必須です。"],
                    "record_date": ["有効な日付を入力してください。"]
                }
            }
        },
        examples=[
            OpenApiExample(
                '体重記録作成例',
                value={
                    "weight": 70.5,
                    "fat": 15.2,
                    "record_date": "2024-01-15T10:30:00Z"
                },
                request_only=True,
                description='体重記録の作成・更新リクエスト例'
            )
        ],
        tags=["体重記録"]
    )
)
class WeightRecordListCreateView(generics.ListCreateAPIView):
    """
    体重記録の取得・作成・更新API

    ユーザーの体重記録を一覧取得・作成・更新するためのAPIです。
    認証が必要で、ログインユーザーの体重記録のみを操作できます。
    同じ日付の記録が既に存在する場合は更新されます。
    """
    serializer_class = WeightRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        自分の体重記録のみ取得

        Returns:
            QuerySet: 認証済みユーザーの体重記録一覧
        """
        return WeightRecord.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        自分の体重を保存。既存のデータがある場合は更新

        Args:
            serializer: バリデーション済みのシリアライザー

        Returns:
            Response: 作成または更新されたデータ

        Business Logic:
            - 同じ日付の記録が存在する場合は更新
            - 存在しない場合は新規作成
            - 更新の場合は200 OK、新規作成の場合は201 Createdを返す
        """
        user = self.request.user
        date = serializer.validated_data.get('record_date')

        existing_record = WeightRecord.objects.filter(user=user, record_date__date=date.date()).first()

        if existing_record:
            existing_record.weight = serializer.validated_data.get('weight', existing_record.weight)
            existing_record.fat = serializer.validated_data.get('fat', existing_record.fat)
            existing_record.save()

            # 更新したデータを返す
            return Response(WeightRecordSerializer(existing_record).data, status=status.HTTP_200_OK)
        else:
            # 新規作成
            serializer.save(user=user)


@extend_schema(
    summary="最新体重記録取得",
    description="ログインユーザーの最新の体重記録を取得します。記録が存在しない場合は404エラーを返します。",
    responses={
        200: WeightRecordSerializer,
        404: {
            "type": "object",
            "properties": {
                "detail": {"type": "string", "description": "エラーメッセージ"}
            },
            "example": {"detail": "体重記録が見つかりません。"}
        }
    },
    tags=["体重記録"]
)
class LatestWeightRecordView(generics.RetrieveAPIView):
    """
    最新体重記録取得API

    ユーザーの最新の体重記録を取得するためのAPIです。
    認証が必要で、ログインユーザーの最新記録のみを取得できます。
    記録が存在しない場合は404エラーを返します。
    """
    serializer_class = WeightRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """
        最新の体重記録を取得

        Returns:
            WeightRecord: 最新の体重記録

        Raises:
            Http404: 記録が存在しない場合
        """
        latest_record = WeightRecord.objects.filter(
            user=self.request.user
        ).order_by('-record_date', '-created_at').first()

        if not latest_record:
            from django.http import Http404
            raise Http404("体重記録が見つかりません。")

        return latest_record
