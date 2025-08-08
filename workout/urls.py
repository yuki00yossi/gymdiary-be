from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkoutSessionViewSet

app_name = 'workout'

# DRF Router for ViewSets
router = DefaultRouter()
router.register(r'', WorkoutSessionViewSet, basename='workout')

urlpatterns = [
    path('', include(router.urls)),
]
