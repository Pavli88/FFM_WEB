from django.contrib import admin
from django.urls import path, include

from . import views
from mysite.views_folder import get_views
from risk.views import *


def my_process():
    print("Initial caching run")


my_process()

get_patterns = [
    path('home/load_robot_stats/<str:env>/', views.load_robot_stats),
    path('exceptions/get/', views.get_exceptions),
    path('home/total_robot_pnl/', views.total_robot_pnl),
    path('home/robot_balances_by_date/', get_views.robot_balances_by_date),
    path('home/get/robot/all/daily_returns/', get_views.all_daily_returns),
]

general_patterns = [
    path('', views.main_page_react),
    path('user_login/', views.login_user),
    path('user_logout/', views.logout_user),
    path('user_register/', views.register),
    path('admin/', admin.site.urls),
    path('', include('reports.urls')),
    path('', include('robots.urls')),
    path('', include('risk.urls')),
    path('', include('signals.urls')),
    path('', include('portfolio.urls')),
    path('', include('accounts.urls')),
    path('', include('trade_app.urls')),
    path('', include('instrument.urls')),
    path('', include('calculations.urls')),
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
    path('test/', views.test),
    path('exceptions/update/', views.update_exception_by_id)
]

urlpatterns = get_patterns + general_patterns
