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


class MySetViewSet(viewsets.ModelViewSet):
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
    permission_classes = [IsAuthenticated]

    def get(self, request, myset_id):
        try:
            myset = MySet.objects.get(id=myset_id, user=request.user)
        except MySet.DoesNotExist:
            return Response({"detail": "マイセットが見つかりません"}, status=status.HTTP_404_NOT_FOUND)

        latest_session = MySetSession.objects.filter(myset=myset).order_by("-date", "-created_at").first()

        if not latest_session:
            return Response({"detail": "記録が存在しません"}, status=status.HTTP_404_NOT_FOUND)

        serializer = MySetSessionDetailSerializer(latest_session)
        return Response(serializer.data)

    def post(self, request, myset_id):
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


# --- 記録一覧 ---
class MySetSessionListView(generics.ListAPIView):
    serializer_class = MySetSessionListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MySetSession.objects.filter(user=self.request.user).order_by('-date')



# --- 記録詳細 ---
class MySetSessionDetailView(generics.RetrieveAPIView):
    serializer_class = MySetSessionDetailSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return MySetSession.objects.filter(user=self.request.user)
