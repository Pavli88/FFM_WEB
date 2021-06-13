from django.urls import path
from . import views
from signals.views import *

urlpatterns = [
    path('robots/', views.robots_main, name="robots main"),
    path('robots/get_robots/', views.load_robots, name="show robots"),
    path('robots/amend_robot/', views.amend_robot, name="amend robot"),
    path('robots/delete_robot/', views.delete_robot, name="delete robot"),
    path('robots/new_robot/', views.new_robot, name="new robot"),
    path('robots/process_hub/', views.robot_process_hub),
    path('robots/signals/trade/', views.incoming_trade),
    path('robots/get_securities/', views.load_securities),
    path('robots/get_accounts/', views.load_accounts),
    path('robots/delete_robot/', views.delete_robot),
    path('home/get_robot_data/<str:data_type>/', views.get_robot_data),
    path('robots/calculate_robot_balance/', views.calculate_robot_balance),
    path('robots/get_robot_balance/<str:type>/', views.get_robot_balances),
]
