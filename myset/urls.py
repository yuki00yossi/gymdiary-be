from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MySetViewSet

app_name = 'myset'

# DRF Router for ViewSets
router = DefaultRouter()
router.register(r'', MySetViewSet, basename='myset')

urlpatterns = [
    path('', include(router.urls)),
]