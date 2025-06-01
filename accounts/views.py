import requests


from django.shortcuts import render
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

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
        refresh = RefreshToken.for_user(validated_data)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'username': validated_data.username,
                'email': validated_data.email,
                'name': validated_data.name,
                'profile_image': validated_data.profile_image.url if validated_data.profile_image else None,
            }
        }, status=status.HTTP_200_OK)


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


class GoogleLoginAPIView(APIView):
    """ GoogleログインAPI """
    permission_classes = [permissions.AllowAny,]

    def post(self, request):
        access_token = request.data.get('access_token')
        if not access_token:
            return Response({"error": "Access token is required."}, status=status.HTTP_400_BAD_REQUEST)

        # GoogleのAPIを使ってユーザー情報を取得
        user_info_url = "https://www.googleapis.com/oauth2/v3/userinfo"
        res = requests.get(
            user_info_url,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10
        )
        if res.status_code != 200:
            return Response({"error": "Failed to fetch user info from Google."}, status=status.HTTP_400_BAD_REQUEST)

        profile = res.json()
        google_id = profile.get("sub")
        email = profile.get("email")
        name = profile.get("name")
        picture = profile.get("picture")
        if not google_id or not email:
            return Response({"error": "Invalid user info from Google."}, status=status.HTTP_400_BAD_REQUEST)

        print("===================================")
        print(f"User profile: {profile}")
        print("===================================")

        user, created = CustomUser.objects.get_or_create(
            email=email,
            defaults={
                "email": email,
                "name": name,
                "profile_image": picture,
                "is_active": True,
                "username": f"google_{google_id}"  # ユーザー名はGoogle IDをベースに生成
            }
        )

        # JWTトークンを生成
        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "username": user.username,
                "email": user.email,
                "name": user.name,
                "profile_image": user.profile_image.url if user.profile_image else None,
            }
        }, status=status.HTTP_200_OK)
