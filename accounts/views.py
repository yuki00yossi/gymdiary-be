from django.shortcuts import render
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import CustomUser
from .serializers import UserRegisterSerializer, UserLoginSerializer, UserSerializer


# Create your views here.
class UserRegisterAPIView(generics.CreateAPIView):
    """ 会員登録API (メンバー or トレーナー選択可能) """
    queryset = CustomUser.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny,]


class UserLoginAPIView(APIView):
    """ ログインAPI(セッション認証) """
    permission_classes = [permissions.AllowAny,]

    def post(self, request):
        """ ポストのみ定義 """
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        login(request, user)
        return Response(
            {'message': 'ログイン成功', 'username': user.username},
            status=status.HTTP_200_OK)


class UserLogoutAPIView(APIView):
    """ ログアウトAPI """
    permission_classes = [permissions.IsAuthenticated,]

    def post(self, request):
        """ ログアウト実行 """
        logout(request)
        return Response({'message': 'ログアウトしました'}, status=status.HTTP_200_OK)


class UserMeAPIView(APIView):
    """ ログインユーザーの情報を取得するAPI """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """ ログイン中ユーザーの情報を返す """
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
