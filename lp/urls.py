# health_hub/urls.py
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name="index"),
]
