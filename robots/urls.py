from django.urls import path
from . import views
from signals.views import *

urlpatterns = [
    path('robots/get_robots/<str:env>/', views.get_robots),
    path('robots/get_robots_with_instrument/', views.get_robots_with_instrument_data),
    path('robots/get_robot/<str:robot>/', views.get_robot),
    path('robots/amend_robot/', views.amend_robot),
    path('robots/delete_robot/', views.delete_robot),
    path('robots/new_robot/', views.new_robot),
    path('robots/calculate_robot_balance/', views.robot_balance_calc),
    path('robots/get_robot_balance/<str:env>/', views.get_robot_balances),
    path('robots/get_balance/', views.get_robot_balance),
    path('robots/drawdown/', views.robot_drawdown),
    path('robots/cumulative_ret/', views.cumulative_return),
    path('robots/pricing/', views.robot_pricing),
    path('robots/get_prices/', views.get_prices),
    path('robots/get_last_price/', views.get_last_price),
    path('robots/trades/', views.get_trades),
    path('robots/robot_cash_flow/<str:robot>/', views.get_robot_cf),
    path('robots/test_socket/', views.test_socket),
]
