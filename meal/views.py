from datetime import date
from itertools import chain
import os, uuid

from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from .models import MealRecord, MealItem, MealRecordItem
from .serializers import MealRecordSerializer, MealItemSerializer
from django.core.files.storage import default_storage
from django.utils.text import slugify
from accounts.utils import generate_presigned_url
from django.db.models import Prefetch


class MealRecordViewSet(viewsets.ModelViewSet):
    """ ユーザーの食事記録のCRUD API """
    serializer_class = MealRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """ ログインユーザーの食事記録のみ取得 """
        if self.request.GET.get('date'):
            return MealRecord.objects.filter(user=self.request.user, date=self.request.GET['date']).order_by("-date")
        return MealRecord.objects.filter(user=self.request.user).order_by("-date")

    def perform_create(self, serializer):
        """ 食事記録を作成（ユーザーを紐づける）"""
        serializer.save(user=self.request.user)

    @action(methods=['get'], detail=False, url_path='summary', url_name='summary')
    def summary(self, request):
        """ 食事記録のサマリーを取得 """
        records = MealRecord.objects.filter(
            user=request.user,
            date=date.today()
        ).prefetch_related(
            Prefetch('meal_items', queryset=MealRecordItem.objects.select_related('meal_item'))
        )

        if not records.exists():
            return Response({})

        # MealRecordごとのmeal_itemsをすべて合体（フラットにする）
        meal_items = list(chain.from_iterable(record.meal_items.all() for record in records))

        # 栄養素を集計（MealItemのカロリー等を使う場合）
        total_calories = sum(item.meal_item.calories * item.quantity for item in meal_items)
        total_protein = sum(item.meal_item.protein * item.quantity for item in meal_items)
        total_fat = sum(item.meal_item.fat * item.quantity for item in meal_items)
        total_carbs = sum(item.meal_item.carbs * item.quantity for item in meal_items)

        return Response({
            "total_calories": total_calories,
            "total_protein": total_protein,
            "total_fat": total_fat,
            "total_carbs": total_carbs,
            "record_count": records.count()
        })


class MealItemViewSet(viewsets.ModelViewSet):
    """ 食品データの取得・作成（更新・削除は不可） """
    serializer_class = MealItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """ 全ての食品データを取得 """
        return MealItem.objects.all()

    def perform_create(self, serializer):
        """ 新しい食品データを作成 """
        serializer.save()

    def update(self, request, *args, **kwargs):
        """ 食品データの更新は禁止 """
        return Response({"detail": "食品データの更新はできません。"}, status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, *args, **kwargs):
        """ 食品データの削除は禁止 """
        return Response({"detail": "食品データの削除はできません。"}, status=status.HTTP_403_FORBIDDEN)


class PhotoUploadView(APIView):
    """ 食事画像アップロード用API """
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        """ POSTリクエスト """
        photo = request.FILES.get('photo')
        if not photo:
            return Response({'error': '画像ファイルがありません。'}, status=400)
        # 拡張子
        ext = os.path.splitext(photo.name)[-1].lower()
        sanitized_name = slugify(os.path.splitext(photo.name)[0])
        # ユーザーID + UUID をファイル名に設定（同じユーザーのファイルでも重複しない）
        unique_filename = f"{request.user.id}-{uuid.uuid4().hex[:8]}-{sanitized_name}{ext}"

        file_path = default_storage.save(f"meals/{unique_filename}", photo)

        return Response({"photo_url": file_path}, status=201)
