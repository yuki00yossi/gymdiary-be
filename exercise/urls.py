from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExerciseViewSet, ExerciseCategoryViewSet

app_name = 'exercise'

# DRF Router for ViewSets
router = DefaultRouter()
router.register(r'exercises', ExerciseViewSet, basename='exercise')
router.register(r'categories', ExerciseCategoryViewSet, basename='exercise-category')

urlpatterns = [
    path('', include(router.urls)),
]