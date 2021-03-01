from django.contrib import admin
from django.urls import path, include
from . import views
from risk.views import *

urlpatterns = [
    path('', views.main_page, name="main_page"),
    path('home/', views.home, name="home_page"),
    path('login/', views.login, name="login"),
    path('logout/', views.logout_user, name="logout"),
    path('register/', views.register, name="register"),
    path('admin/', admin.site.urls),
    path('', include('reports.urls')),
    path('', include('robots.urls')),
    path('', include('risk.urls')),
    path('', include('signals.urls')),
    path('', include('portfolio.urls')),
    path('', include('accounts.urls')),
    path('', include('trade_app.urls')),
    path('', include('instrument.urls')),
    path('save_home/', views.save_layout, name="make_default"),
    path('settings/', views.go_to_settings, name="settings main"),
    path('settings/save/', views.save_settings, name="save settings"),
    path('home/load_robot_stats/', views.load_robot_stats),
    path('home/get_messages/', views.get_messages),
    path('home/test_calc/', views.test_calc),
    path('home/get_robot_risk/', get_robot_risk),
    path('home/update/risk_per_trade/', update_risk_per_trade),
]
