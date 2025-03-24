# health_hub/urls.py
from django.urls import path, include
from . import views
from wagtail import urls as wagtail_urls

urlpatterns = [
    path('recipes/search/', views.RecipeSearchView.as_view(), name="recipe.search"),
    path('recipes/<int:pk>', views.RecipeDetailView.as_view(), name="recipe.detail"),
    path('', include(wagtail_urls)),
]
