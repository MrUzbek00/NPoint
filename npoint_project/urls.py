"""
URL configuration for npoint_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from npoint_app.api import JSONDataViewSet
from npoint_app.api import MyViewSet

router = DefaultRouter()
router.register(r"public/json", JSONDataViewSet, basename="public-json")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('npoint_app.urls')),
    path('api/', include(router.urls)),
    path('api/<str:username>/<slug:slug>/<int:json_id>/', MyViewSet.as_view({'get': 'list'}), name='public-json-content'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)