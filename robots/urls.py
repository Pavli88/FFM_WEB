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
    path('robots/get_brokers/', views.get_brokers),
    path('robots/get_securities/', views.load_securities),
    path('robots/get_accounts/', views.load_accounts),
    path('robots/delete_robot/', views.delete_robot),
    path('robots/calculate_robot_balance/', views.calculate_robot_balance),
]
