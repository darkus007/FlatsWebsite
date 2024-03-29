"""website URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title="API Сайта с квартирами",
        default_version="v1",
        description="Предоставляет REST API для работы с сайтом",
        contact=openapi.Contact(email="darkus007@yandex.ru"),
    ), public=True, permission_classes=[permissions.AllowAny, ],
)

handler404 = 'flats.views.page_not_found'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('flats.urls')),
    path('members/', include('members.urls')),
    path('members/', include('django.contrib.auth.urls')),
    path('captcha/', include('captcha.urls')),
    path('api/v1/', include('api.urls')),
    path('api/v1/auth/', include('rest_framework.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
