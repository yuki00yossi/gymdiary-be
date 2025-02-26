from django.urls import path
from .views import (
    UserRegisterAPIView,
    UserLoginAPIView,
    UserLogoutAPIView,
    UserMeAPIView)


urlpatterns = [
    path('register/', UserRegisterAPIView.as_view(), name='api.register'),
    path('login/', UserLoginAPIView.as_view(), name='api.login'),
    path('logout/', UserLogoutAPIView.as_view(), name='api.logout'),
    path('me/', UserMeAPIView.as_view(), name='api.me'),
]
