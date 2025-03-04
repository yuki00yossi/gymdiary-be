from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MealRecordViewSet, MealItemViewSet

router = DefaultRouter()
router.register(r"", MealRecordViewSet, basename="meal")
router.register(r"items", MealItemViewSet, basename="meal-item")

urlpatterns = [
    path("", include(router.urls)),
]
