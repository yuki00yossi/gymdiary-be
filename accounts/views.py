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

from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes


# Create your views here.
@extend_schema(
    summary="会員登録",
    description="新しいユーザーアカウントを作成します。メンバーまたはトレーナーとして登録できます。",
    request=UserRegisterSerializer,
    responses={
        201: UserRegisterSerializer,
        400: {
            "type": "object",
            "properties": {
                "field_name": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "バリデーションエラーメッセージ"
                }
            }
        }
    },
    tags=["認証"]
)
class UserRegisterAPIView(generics.CreateAPIView):
    """ 会員登録API (メンバー or トレーナー選択可能) """
    queryset = CustomUser.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny,]


class EmailVerificationAPIView(APIView):
    """ メール認証API """
    permission_classes = [permissions.AllowAny,]

    @extend_schema(
        summary="メール認証トークン送信",
        description="指定したユーザー名のユーザーにメール認証トークンを送信します。既存のトークンがある場合は削除して新しく発行します。",
        request=EmailVerificationSerializer,
        responses={
            200: {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "成功メッセージ"}
                },
                "example": {"message": "メール認証用のトークンを送信しました"}
            },
            400: {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "エラーメッセージ"}
                },
                "example": {"message": "不正なリクエストです。"}
            }
        },
        tags=["認証"]
    )
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

    @extend_schema(
        summary="メール認証トークン検証",
        description="メール認証トークンを検証してユーザーアカウントを有効化します。",
        request=EmailVerificationSerializer,
        responses={
            200: {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "成功メッセージ"}
                },
                "example": {"message": "メール認証が完了しました"}
            },
            400: {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "エラーメッセージ"}
                },
                "examples": {
                    "invalid_request": {
                        "summary": "不正なリクエスト",
                        "value": {"message": "不正なリクエストです。"}
                    },
                    "invalid_token": {
                        "summary": "無効なトークン",
                        "value": {"message": "無効なトークンです"}
                    }
                }
            }
        },
        tags=["認証"]
    )
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


@extend_schema(
    summary="ログイン",
    description="ユーザー認証を行い、JWTトークン（access/refresh）を取得します。",
    request=UserLoginSerializer,
    responses={
        200: {
            "type": "object",
            "properties": {
                "refresh": {"type": "string", "description": "リフレッシュトークン"},
                "access": {"type": "string", "description": "アクセストークン"},
                "user": {
                    "type": "object",
                    "properties": {
                        "username": {"type": "string", "description": "ユーザー名"},
                        "email": {"type": "string", "description": "メールアドレス"},
                        "name": {"type": "string", "description": "表示名"},
                        "profile_image": {"type": "string", "description": "プロフィール画像URL", "nullable": True}
                    }
                }
            },
            "example": {
                "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                "user": {
                    "username": "testuser",
                    "email": "test@example.com",
                    "name": "テストユーザー",
                    "profile_image": "https://example.com/profile.jpg"
                }
            }
        },
        403: {
            "type": "object",
            "properties": {
                "message": {"type": "string", "description": "エラーメッセージ"}
            }
        }
    },
    tags=["認証"]
)
class UserLoginAPIView(APIView):
    """ ログインAPI(JWT認証) """
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


@extend_schema(
    summary="ログアウト",
    description="ユーザーをログアウトします。",
    responses={
        200: {
            "type": "object",
            "properties": {
                "message": {"type": "string", "description": "成功メッセージ"}
            },
            "example": {"message": "ログアウトしました"}
        }
    },
    tags=["認証"]
)
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

    @extend_schema(
        summary="ログインユーザー情報取得",
        description="現在ログイン中のユーザーの詳細情報を取得します。",
        responses={200: UserSerializer},
        tags=["ユーザー"]
    )
    def get(self, request):
        """ ログイン中ユーザーの情報を返す """
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        """ ログイン中ユーザーの情報を更新する """
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


@ensure_csrf_cookie
def get_csrf_token(request):
    """ CSRFトークンをcookieにセットするAPI """
    return JsonResponse({"csrfToken": request.META.get('CSRF_COOKIE')})


@extend_schema(
    summary="Googleログイン",
    description="GoogleのOAuth2アクセストークンを使用してログインし、JWTトークンを取得します。",
    request={
        "type": "object",
        "properties": {
            "access_token": {"type": "string", "description": "GoogleのOAuth2アクセストークン"}
        },
        "required": ["access_token"]
    },
    responses={
        200: {
            "type": "object",
            "properties": {
                "refresh": {"type": "string", "description": "リフレッシュトークン"},
                "access": {"type": "string", "description": "アクセストークン"},
                "user": {
                    "type": "object",
                    "properties": {
                        "username": {"type": "string", "description": "ユーザー名"},
                        "email": {"type": "string", "description": "メールアドレス"},
                        "name": {"type": "string", "description": "表示名"},
                        "profile_image": {"type": "string", "description": "プロフィール画像URL", "nullable": True}
                    }
                }
            },
            "example": {
                "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                "user": {
                    "username": "google_123456789",
                    "email": "user@gmail.com",
                    "name": "Google User",
                    "profile_image": "https://lh3.googleusercontent.com/..."
                }
            }
        },
        400: {
            "type": "object",
            "properties": {
                "error": {"type": "string", "description": "エラーメッセージ"}
            },
            "examples": {
                "missing_token": {
                    "summary": "アクセストークンなし",
                    "value": {"error": "Access token is required."}
                },
                "invalid_token": {
                    "summary": "無効なトークン",
                    "value": {"error": "Failed to fetch user info from Google."}
                },
                "invalid_user_info": {
                    "summary": "無効なユーザー情報",
                    "value": {"error": "Invalid user info from Google."}
                }
            }
        }
    },
    tags=["認証"]
)
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
