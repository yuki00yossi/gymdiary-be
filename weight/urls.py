from django.urls import path
from .views import WeightRecordListCreateView, LatestWeightRecordView

# Weight API URLs
#
# 体重記録のAPIエンドポイントを定義します。
#
# Endpoints:
#   - /api/weight/ (GET, POST): 体重記録の一覧取得・作成・更新
#   - /api/weight/latest/ (GET): 最新の体重記録取得
#
# Authentication:
#   - すべてのエンドポイントで認証が必要
#   - ユーザーは自分のデータのみアクセス可能
#
# Tags: 体重記録

urlpatterns = [
    path('', WeightRecordListCreateView.as_view(), name='weight-list'),
    path('latest/', LatestWeightRecordView.as_view(), name='weight-latest'),
]
