from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home),
    path('admin/', admin.site.urls),
    path('', include('reports.urls')),
    path('', include('robots.urls')),
    path('', include('risk.urls')),
]
