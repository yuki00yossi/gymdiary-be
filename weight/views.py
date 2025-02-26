from rest_framework import generics, permissions
from .models import WeightRecord
from .serializers import WeightRecordSerializer


# Create your views here.
class WeightRecordListCreateView(generics.ListCreateAPIView):
    """ 体重記録の取得＆作成 """
    serializer_class = WeightRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """ 自分のデータのみ取得可能 """
        return WeightRecord.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """ 自分の体重を保存 """
        serializer.save(user=self.request.user)

