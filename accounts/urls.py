from django.urls import path
from .views import (
    UserRegisterAPIView,
    UserLoginAPIView,
    UserLogoutAPIView,
    UserMeAPIView,
    EmailVerificationAPIView, get_csrf_token)


urlpatterns = [
    path('csrf/', get_csrf_token, name='api.csrf'),
    path('register/', UserRegisterAPIView.as_view(), name='api.register'),
    path('login/', UserLoginAPIView.as_view(), name='api.login'),
    path('logout/', UserLogoutAPIView.as_view(), name='api.logout'),
    path('verify-email/', EmailVerificationAPIView.as_view(), name='api.email.verify'),
    path('verify-email/resend/', EmailVerificationAPIView.as_view(), name='api.email.verify.resend'),
    path('me/', UserMeAPIView.as_view(), name='api.me'),
]
