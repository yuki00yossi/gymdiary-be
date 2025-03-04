from rest_framework import generics, permissions
from .models import TrainingSession
from .serializers import TrainingSessionSerializer


# Create your views here.
class TrainingSessionListCreateView(generics.ListCreateAPIView):
    """ トレーニング記録の取得＆作成 """
    serializer_class = TrainingSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """ 自分のトレーニング記録のみ記録 """
        return TrainingSession.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """ トレーニング記録を作成(ログインユーザーに紐づけ) """
        serializer.save(user=self.request.user)


class TrainingSessionDetailView(generics.RetrieveDestroyAPIView):
    """ トレーニング記録の詳細取得・削除 """
    serializer_class = TrainingSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TrainingSession.objects.filter(user=self.request.user)
