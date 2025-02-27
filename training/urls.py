from django.urls import path
from .views import TrainingSessionListCreateView, TrainingSessionDetailView


urlpatterns = [
    path('', TrainingSessionListCreateView.as_view(), name='training-list'),
    path('<int:pk>/', TrainingSessionDetailView.as_view(), name='training-detail'),
]

