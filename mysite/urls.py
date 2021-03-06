from django.contrib import admin
from django.urls import path, include
from . import views
from signals.views import *

urlpatterns = [
    path('', views.home, name="home_page"),
    path('admin/', admin.site.urls),
    path('create_broker/', views.create_broker, name="create broker account"),
    path('', include('reports.urls')),
    path('', include('robots.urls')),
    path('', include('risk.urls')),
    path('', include('signals.urls')),
    path('', include('portfolio.urls')),
    path('new_trade/', new_execution, name="test_execution"),
    path('close_trade', close_all_trades, name="test_close_execution"),
]
