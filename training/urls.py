from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (TrainingSessionListCreateView, TrainingSessionDetailView,
                    MySetRecordView, MySetViewSet, MySetSessionListView,
                    MySetSessionDetailView)


router = DefaultRouter()
router.register('', MySetViewSet, basename='myset')

urlpatterns = [
    path('', TrainingSessionListCreateView.as_view(), name='training-list'),
    path('<int:pk>/', TrainingSessionDetailView.as_view(), name='training-detail'),
    path('mysets/records/', MySetSessionListView.as_view(), name='myset-records-list'),
    path('mysets/records/<int:id>/', MySetSessionDetailView.as_view(), name='myset-records-detail'),
    path('mysets/<int:myset_id>/record/', MySetRecordView.as_view(), name='myset'),
    path('mysets/', include(router.urls), name='myset'),
]
