from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MealRecordViewSet, MealItemViewSet, PhotoUploadView

router = DefaultRouter()
router.register(r"items", MealItemViewSet, basename="meal-item")
router.register(r"", MealRecordViewSet, basename="meal")

urlpatterns = [
    path("photo/", PhotoUploadView.as_view(), name="meal.upload.photo"),
    path("", include(router.urls)),
]
