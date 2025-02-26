from django.urls import path
from .views import WeightRecordListCreateView

urlpatterns = [
    path('', WeightRecordListCreateView.as_view(), name='weight-list'),
]
