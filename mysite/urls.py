from django.contrib import admin
from django.urls import path, include
from . import views
from risk.views import *

def my_process():
    print("Initial caching run")

my_process()

urlpatterns = [
    path('', views.main_page_react),
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
    path('home/system_messages/<str:type>/', system_messages),
    path('home/verify_sys_msg/<str:msg_id>/', verify_system_message),
    path('new_task/', views.new_task),
    path('new/schedule/', views.new_schedule),
    path('delete/schedule/', views.delete_schedule),
    path('update_task/', views.update_task),
    path('home/daily_robot_balances/', views.aggregated_robot_pnl_by_date),
    path('home/robot_pnl/', views.aggregated_robot_pnl),
    path('home/total_robot_pnl/', views.total_robot_pnl),
    path('home/total_robot_balances_by_date/', views.total_robot_balances_by_date),
    path('test/', views.test),
    path('exceptions/get/', views.get_exceptions)
]
