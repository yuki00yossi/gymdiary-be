from django.shortcuts import render
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.utils import generate_token
from .models import CustomUser, EmailVerification
from .serializers import EmailVerificationSerializer, UserRegisterSerializer, UserLoginSerializer, UserSerializer


# Create your views here.
class UserRegisterAPIView(generics.CreateAPIView):
    """ 会員登録API (メンバー or トレーナー選択可能) """
    queryset = CustomUser.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny,]


class EmailVerificationAPIView(APIView):
    """ メール認証API """
    permission_classes = [permissions.AllowAny,]

    def put(self, request):
        """ メール認証トークンを送信する

        すでにトークン作成済みの場合は削除して、新たに発行する
        """
        serializer = EmailVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        user = CustomUser.objects.filter(username=username).first()

        if user is None:
            return Response({'message': '不正なリクエストです。'}, status=status.HTTP_400_BAD_REQUEST)

        # すでにトークンが存在する場合は削除
        EmailVerification.objects.filter(user=user).delete()

        # 新たにトークンを生成し、メール送信する
        verification = EmailVerification.objects.create(user=user, token=generate_token())
        verification.send_verification_email()

        return Response({'message': 'メール認証用のトークンを送信しました'}, status=status.HTTP_200_OK)

    def post(self, request):
        """ メール認証トークンを検証する """
        serializer = EmailVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data.get('token')
        username = serializer.validated_data.get('username')
        user = CustomUser.objects.filter(username=username).first()

        if user is None:
            return Response({'message': '不正なリクエストです。'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            verification = EmailVerification.objects.get(user=user, token=token)
            verification.user.is_active = True
            verification.user.save()
            verification.delete()
            return Response({'message': 'メール認証が完了しました'}, status=status.HTTP_200_OK)
        except EmailVerification.DoesNotExist:
            return Response({'message': '無効なトークンです'}, status=status.HTTP_400_BAD_REQUEST)


class UserLoginAPIView(APIView):
    """ ログインAPI(セッション認証) """
    permission_classes = [permissions.AllowAny,]

    def post(self, request):
        """ ポストのみ定義 """
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        if isinstance(validated_data, dict):
            return Response(
                validated_data, status=status.HTTP_403_FORBIDDEN)
        login(request, validated_data)
        return Response(
            {'message': 'ログイン成功', 'username': validated_data.username},
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


@ensure_csrf_cookie
def get_csrf_token(request):
    """ CSRFトークンをcookieにセットするAPI """
    return JsonResponse({"csrfToken": request.META.get('CSRF_COOKIE')})
