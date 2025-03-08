from rest_framework import generics, permissions, status
from rest_framework.response import Response
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
        """ 自分の体重を保存。既存のデータがある場合は更新 """
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
