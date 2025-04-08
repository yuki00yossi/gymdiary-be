from django.urls import path
from .views import (
    UserRegisterAPIView,
    UserLoginAPIView,
    UserLogoutAPIView,
    UserMeAPIView,
    EmailVerificationAPIView, ensure_csrf_cookie)


urlpatterns = [
    path('csrf/', ensure_csrf_cookie, name='api.csrf'),
    path('register/', UserRegisterAPIView.as_view(), name='api.register'),
    path('login/', UserLoginAPIView.as_view(), name='api.login'),
    path('logout/', UserLogoutAPIView.as_view(), name='api.logout'),
    path('verify-email/', EmailVerificationAPIView.as_view(), name='api.email.verify'),
    path('verify-email/resend/', EmailVerificationAPIView.as_view(), name='api.email.verify.resend'),
    path('me/', UserMeAPIView.as_view(), name='api.me'),
]
