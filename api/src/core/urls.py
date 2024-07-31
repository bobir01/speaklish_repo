"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

from core import settings

schema_view = get_schema_view(
    openapi.Info(
        title="Speaklish API",
        default_version='v1',
        description="Speaklish API",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="b.mardonov@speaklish.uz"),
        url="https://api.speaklish.uz",
    ),
    public=True,
    permission_classes=[permissions.IsAuthenticated, ],
    authentication_classes=[BasicAuthentication, ],
)

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),
    path('', include('api.urls'), name='api'),
    path('school/', include('school_api.urls'), name='school'),
    path('api-auth/', include('rest_framework.urls'), name='rest_framework'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('questions/', include('questions.urls'), name='questions_urls'),
    path('writing/', include('writing_checker.urls'), name='writing_checker_urls'),
    path('payments/', include('payments.urls'), name='payments_urls'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
