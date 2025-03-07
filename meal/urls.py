from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MealRecordViewSet, MealItemViewSet

router = DefaultRouter()
router.register(r"items", MealItemViewSet, basename="meal-item")
router.register(r"", MealRecordViewSet, basename="meal")

urlpatterns = [
    path("", include(router.urls)),
]
