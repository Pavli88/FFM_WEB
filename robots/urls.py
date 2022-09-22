from django.urls import path
from . import views
from .views_folder import calculation_views, get_views, delete_views
from signals.views import *

urlpatterns = [
    path('robots/calculate/monthly_return/', calculation_views.monthly_return),
    path('robots/calculate/balance/', calculation_views.robot_balance),
    path('robots/delete/transaction/', delete_views.delete_transaction),
    path('robots/get/monthly_returns/', get_views.monthly_returns),
    path('robots/get_robot_data/', views.get_robot_data),
    path('robots/get_robots/<str:env>/', views.get_robots),
    path('robots/get_robots_with_instrument/', views.get_robots_with_instrument_data),
    path('robots/get_robot/<str:robot>/', views.get_robot),
    path('robots/update_robot/', views.update_robot),
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
    path('robots/get/cash_flow/<str:robot>/', views.get_robot_cf),
    path('robots/update_strategy_params/', views.update_strategy_params),
    path('robots/update/general/', views.update_robot),
    path('robots/monthly_returns_calc/', views.monthly_returns_calculation),

]
