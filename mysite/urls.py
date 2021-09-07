from django.contrib import admin
from django.urls import path, include
from . import views
from risk.views import *

urlpatterns = [
    path('', views.main_page, name="main_page"),
    path('react/', views.main_page_react),
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
    path('home/load_robot_stats/<str:env>/', views.load_robot_stats),
    path('home/get_robot_risk/', get_robot_risk),
    path('home/update/risk_per_trade/', update_risk_per_trade),
    path('home/system_messages/', system_messages),
    path('new_task/', views.new_task),
    path('kill_task/', views.kill_task),
]
