from datetime import date
from itertools import chain
import os, uuid

from rest_framework import viewsets, permissions
from rest_framework.views import APIView, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from .models import MealRecord, MealItem, MealRecordItem
from .serializers import MealRecordSerializer, MealItemSerializer
from django.core.files.storage import default_storage
from django.utils.text import slugify
from accounts.utils import generate_presigned_url
from django.db.models import Prefetch, Q

from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes


@extend_schema_view(
    list=extend_schema(
        summary="食事記録一覧取得",
        description="ログインユーザーの食事記録一覧を取得します。日付でフィルタリングも可能です。",
        parameters=[
            OpenApiParameter(
                name='date',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='取得したい日付（YYYY-MM-DD形式）',
                examples=[
                    OpenApiExample('今日の記録', value='2024-01-15'),
                ]
            ),
        ],
        tags=["食事記録"]
    ),
    create=extend_schema(
        summary="食事記録作成",
        description="新しい食事記録を作成します。ユーザーは自動的に紐づけられます。",
        tags=["食事記録"]
    ),
    retrieve=extend_schema(
        summary="食事記録詳細取得",
        description="指定したIDの食事記録の詳細を取得します。",
        tags=["食事記録"]
    ),
    update=extend_schema(
        summary="食事記録更新",
        description="指定したIDの食事記録を更新します。",
        tags=["食事記録"]
    ),
    partial_update=extend_schema(
        summary="食事記録部分更新",
        description="指定したIDの食事記録を部分的に更新します。",
        tags=["食事記録"]
    ),
    destroy=extend_schema(
        summary="食事記録削除",
        description="指定したIDの食事記録を削除します。",
        tags=["食事記録"]
    )
)
class MealRecordViewSet(viewsets.ModelViewSet):
    """
    食事記録の管理API

    ユーザーの食事記録を作成、取得、更新、削除するためのAPIです。
    認証が必要で、ログインユーザーの食事記録のみを操作できます。

    主な機能:
    - 食事記録の一覧取得（日付フィルタリング可能）
    - 食事記録の作成
    - 食事記録の更新
    - 食事記録の削除
    - 日次栄養サマリーの取得

    認証: 必須（IsAuthenticated）
    """
    serializer_class = MealRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        ログインユーザーの食事記録を取得

        クエリパラメータ:
            date (str, optional): 特定の日付の記録を取得（YYYY-MM-DD形式）
                                 例: ?date=2024-01-15

        Returns:
            QuerySet: ログインユーザーの食事記録（日付の降順）
        """
        if self.request.GET.get('date'):
            return MealRecord.objects.filter(user=self.request.user, date=self.request.GET['date']).order_by("-date")
        return MealRecord.objects.filter(user=self.request.user).order_by("-date")

    def perform_create(self, serializer):
        """
        食事記録を作成（ユーザーを自動で紐づける）

        Args:
            serializer: MealRecordSerializer
        """
        serializer.save(user=self.request.user)

    @extend_schema(
        summary="指定日の栄養サマリー取得",
        description="指定した日付のすべての食事記録から栄養素を集計して返します。朝食、昼食、夕食、間食別のカロリーも含まれます。日付が指定されない場合は本日のデータを返します。",
        parameters=[
            OpenApiParameter(
                name='date',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='取得したい日付（YYYY-MM-DD形式）。指定しない場合は本日',
                required=False,
                examples=[
                    OpenApiExample('今日の記録', value='2024-01-15'),
                    OpenApiExample('昨日の記録', value='2024-01-14'),
                ]
            ),
        ],
        responses={
            200: {
                "type": "object",
                "properties": {
                    "total_calories": {"type": "number", "description": "総カロリー (kcal)"},
                    "total_protein": {"type": "number", "description": "総タンパク質 (g)"},
                    "total_fat": {"type": "number", "description": "総脂質 (g)"},
                    "total_carbs": {"type": "number", "description": "総炭水化物 (g)"},
                    "record_count": {"type": "integer", "description": "食事記録数"},
                    "meal_type_calories": {
                        "type": "object",
                        "properties": {
                            "朝食": {"type": "number", "description": "朝食のカロリー (kcal)"},
                            "昼食": {"type": "number", "description": "昼食のカロリー (kcal)"},
                            "夕食": {"type": "number", "description": "夕食のカロリー (kcal)"},
                            "間食": {"type": "number", "description": "間食のカロリー (kcal)"}
                        },
                        "description": "食事タイプ別のカロリー"
                    },
                    "date": {"type": "string", "description": "取得した日付（YYYY-MM-DD形式）"}
                },
                "example": {
                    "total_calories": 2100.5,
                    "total_protein": 120.3,
                    "total_fat": 85.7,
                    "total_carbs": 250.8,
                    "record_count": 3,
                    "meal_type_calories": {
                        "朝食": 450.2,
                        "昼食": 650.8,
                        "夕食": 750.3,
                        "間食": 249.2
                    },
                    "date": "2024-01-15"
                }
            }
        },
        tags=["食事記録"]
    )
    @action(methods=['get'], detail=False, url_path='summary', url_name='summary')
    def summary(self, request):
        """指定日の食事記録の栄養サマリーを取得"""
        # 日付パラメータを取得（デフォルトは今日）
        target_date = request.query_params.get('date')
        if target_date:
            try:
                target_date = date.fromisoformat(target_date)
            except ValueError:
                return Response(
                    {"error": "日付形式が正しくありません。YYYY-MM-DD形式で入力してください。"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            target_date = date.today()

        records = MealRecord.objects.filter(
            user=request.user,
            date=target_date
        ).prefetch_related(
            Prefetch('meal_items', queryset=MealRecordItem.objects.select_related('meal_item'))
        )

        if not records.exists():
            return Response({
                "total_calories": 0.0,
                "total_protein": 0.0,
                "total_fat": 0.0,
                "total_carbs": 0.0,
                "record_count": 0,
                "meal_type_calories": {
                    "朝食": 0.0,
                    "昼食": 0.0,
                    "夕食": 0.0,
                    "間食": 0.0
                },
                "date": target_date.isoformat()
            })

        # 食事タイプ別のカロリーを初期化
        meal_type_calories = {
            "朝食": 0.0,
            "昼食": 0.0,
            "夕食": 0.0,
            "間食": 0.0
        }

        # 総栄養素を初期化
        total_calories = 0.0
        total_protein = 0.0
        total_fat = 0.0
        total_carbs = 0.0

        # 各食事記録を処理
        for record in records:
            record_calories = 0.0

            # その記録の各食品のカロリーを計算
            for meal_item in record.meal_items.all():
                # base_quantityあたりの値なので、実際の摂取量に応じて計算
                # 例: base_quantity=100g, calories=200kcal, quantity=150gの場合
                # 実際のカロリー = 200 * (150/100) = 300kcal
                ratio = meal_item.quantity / meal_item.meal_item.base_quantity
                item_calories = meal_item.meal_item.calories * ratio
                record_calories += item_calories

                # 総栄養素に加算
                total_calories += item_calories
                total_protein += meal_item.meal_item.protein * ratio
                total_fat += meal_item.meal_item.fat * ratio
                total_carbs += meal_item.meal_item.carbs * ratio

            # 食事タイプ別のカロリーに加算
            meal_type_calories[record.time_of_day] += record_calories

        return Response({
            "total_calories": total_calories,
            "total_protein": total_protein,
            "total_fat": total_fat,
            "total_carbs": total_carbs,
            "record_count": records.count(),
            "meal_type_calories": meal_type_calories,
            "date": target_date.isoformat()
        })


@extend_schema_view(
    list=extend_schema(
        summary="食品データ一覧取得",
        description="食品データベースから食品情報を取得します。検索キーワードでフィルタリング可能です。",
        parameters=[
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='食品名または検索キーワードで検索',
                examples=[
                    OpenApiExample('鶏肉で検索', value='鶏肉'),
                    OpenApiExample('ご飯で検索', value='ご飯'),
                ]
            ),
        ],
        tags=["食品データ"]
    ),
    create=extend_schema(
        summary="カスタム食品作成",
        description="新しいカスタム食品データを作成します。",
        tags=["食品データ"]
    ),
    retrieve=extend_schema(
        summary="食品データ詳細取得",
        description="指定したIDの食品データの詳細を取得します。",
        tags=["食品データ"]
    ),
    update=extend_schema(
        summary="食品データ更新（禁止）",
        description="食品データの更新は禁止されています。",
        responses={403: {"description": "更新は許可されていません"}},
        tags=["食品データ"]
    ),
    partial_update=extend_schema(
        summary="食品データ部分更新（禁止）",
        description="食品データの部分更新は禁止されています。",
        responses={403: {"description": "更新は許可されていません"}},
        tags=["食品データ"]
    ),
    destroy=extend_schema(
        summary="食品データ削除（禁止）",
        description="食品データの削除は禁止されています。",
        responses={403: {"description": "削除は許可されていません"}},
        tags=["食品データ"]
    )
)
class MealItemViewSet(viewsets.ModelViewSet):
    """
    食品データ管理API

    食品データベースの食品情報を取得・作成するためのAPIです。
    食品データの更新・削除は制限されています。

    主な機能:
    - 食品データの一覧取得（検索機能付き）
    - 食品データの詳細取得
    - 新しい食品データの作成

    制限事項:
    - 食品データの更新は禁止
    - 食品データの削除は禁止

    認証: 必須（IsAuthenticated）
    """
    serializer_class = MealItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        食品データを取得（検索機能付き）

        クエリパラメータ:
            search (str, optional): 食品名または検索キーワードで検索
                                   例: ?search=鶏肉

        Returns:
            QuerySet: 食品データ一覧（検索条件でフィルタリング済み）

        検索対象:
        - 食品名（name）
        - 検索キーワード（search_keywords）
        """
        queryset = MealItem.objects.all()
        search_query = self.request.query_params.get('search', None)
        if search_query:
            # 検索キーワードでフィルタリング
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(search_keywords__icontains=search_query)
            )
        return queryset

    def perform_create(self, serializer):
        """
        新しい食品データを作成

        Args:
            serializer: MealItemSerializer
        """
        serializer.save()

    def update(self, request, *args, **kwargs):
        """
        食品データの更新は禁止

        Returns:
            Response: 403 Forbidden エラー
        """
        return Response({"detail": "食品データの更新はできません。"}, status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, *args, **kwargs):
        """
        食品データの削除は禁止

        Returns:
            Response: 403 Forbidden エラー
        """
        return Response({"detail": "食品データの削除はできません。"}, status=status.HTTP_403_FORBIDDEN)


class PhotoUploadView(APIView):
    """
    食事画像アップロードAPI

    食事の写真をアップロードするためのAPIです。
    アップロードされた画像はS3などのストレージに保存され、
    ファイルパスが返されます。

    URL: /meal/photo-upload/
    Method: POST
    Content-Type: multipart/form-data

    認証: 必須（DRFのデフォルト認証）
    """
    parser_classes = [MultiPartParser]

    @extend_schema(
        summary="食事画像アップロード",
        description="食事の写真をアップロードします。アップロードされた画像はストレージに保存され、ファイルパスが返されます。",
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'photo': {
                        'type': 'string',
                        'format': 'binary',
                        'description': 'アップロードする画像ファイル'
                    }
                },
                'required': ['photo']
            }
        },
        responses={
            201: {
                "type": "object",
                "properties": {
                    "photo_url": {"type": "string", "description": "アップロードされた画像のファイルパス"}
                },
                "example": {
                    "photo_url": "meals/123-abc12345-chicken-dinner.jpg"
                }
            },
            400: {
                "type": "object",
                "properties": {
                    "error": {"type": "string", "description": "エラーメッセージ"}
                },
                "example": {
                    "error": "画像ファイルがありません。"
                }
            }
        },
        tags=["食事画像"]
    )
    def post(self, request, *args, **kwargs):
        """
        食事画像をアップロード

        Args:
            photo (file): アップロードする画像ファイル

        Returns:
            Response: アップロード結果

            成功時のレスポンス例:
            {
                "photo_url": "meals/123-abc12345-chicken-dinner.jpg"
            }

            エラー時のレスポンス例:
            {
                "error": "画像ファイルがありません。"
            }

        Notes:
            - ファイル名は自動的にサニタイズされ、ユニークな名前が生成されます
            - 形式: "{user_id}-{uuid}-{sanitized_name}.{ext}"
            - 保存先: meals/ ディレクトリ
        """
        photo = request.FILES.get('photo')
        if not photo:
            return Response({'error': '画像ファイルがありません。'}, status=400)

        # 拡張子を取得
        ext = os.path.splitext(photo.name)[-1].lower()
        sanitized_name = slugify(os.path.splitext(photo.name)[0])

        # ユーザーID + UUID をファイル名に設定（同じユーザーのファイルでも重複しない）
        unique_filename = f"{request.user.id}-{uuid.uuid4().hex[:8]}-{sanitized_name}{ext}"

        file_path = default_storage.save(f"meals/{unique_filename}", photo)

        return Response({"photo_url": file_path}, status=201)
