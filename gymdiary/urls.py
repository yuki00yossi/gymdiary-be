"""
URL configuration for gymdiary project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from wagtail.admin import urls as wagtailadmin_urls

urlpatterns = [
    path('', include('lp.urls')),
    # wagtail関連
    path('health-hub/', include('health_hub.urls')),
    path('admin/health-hub', include(wagtailadmin_urls)),


    # 各種API
    path('api/account/', include('accounts.urls')),
    path('api/weight/', include('weight.urls')),
    path('api/training/', include('training.urls')),
    path('api/meal/', include('meal.urls')),
    path('api/trainers/', include('trainers.urls')),

    # 管理画面
    path('admin/', admin.site.urls),

    # APIドキュメント関連
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
