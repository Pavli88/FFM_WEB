from django.urls import path
from . import views
from signals.views import *

urlpatterns = [
    path('robots/get_robots/<str:env>/', views.get_robots),
    path('robots/amend_robot/', views.amend_robot),
    path('robots/delete_robot/', views.delete_robot),
    path('robots/new_robot/', views.new_robot),
    path('robots/signals/trade/', views.incoming_trade),
    path('robots/calculate_robot_balance/', views.robot_balance_calc),
    path('robots/get_robot_balance/<str:env>/', views.get_robot_balances),
]
