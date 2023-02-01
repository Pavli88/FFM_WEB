from django.urls import path
from . import views
from .views_folder import calculation_views, get_views, delete_views, update_views, create_views
from signals.views import *

create_views = [
    path('robots/create/strategy/', create_views.create_robot_strategy),
    path('robots/create/robot/', create_views.create_robot),
]

get_patterns = [
    path('robots/get/monthly_returns/', get_views.monthly_returns),
    path('robots/get/robots/<str:env>/', get_views.get_robots),
    path('robots/get/strategy_id/', get_views.get_robots_by_strategy_id),
    path('robots/get/strategies/', get_views.get_strategies),
    path('robots/get/robot/<str:id>/', get_views.get_robot),
    path('robots/get/balance/', get_views.get_robot_balance),
    path('robots/get/transactions/', get_views.transactions),
    path('robots/get/drawdown/', views.robot_drawdown),
    path('robots/get/pnls/', get_views.all_pnl_series),
    path('robots/get/active/<str:env>/', get_views.get_active_robots),
    path('robots/get/all/drawdown/', get_views.all_robots_drawdown),
    path('robots/get/exposures/', get_views.get_robot_exposures),
]

update_patterns = [
    path('robots/update/robot/', update_views.update_robot),
    path('robots/update/strategy/', update_views.update_robot_strategy),
]

delete_patterns = [
    path('robots/delete/transaction/', delete_views.delete_transaction),
]

calculate_patterns = [
    path('robots/calculate/monthly_return/', calculation_views.monthly_return),
    path('robots/calculate/balance/', calculation_views.robot_balance),
]

other_patterns = [
    path('robots/get_robot_data/', views.get_robot_data),
    path('robots/get_robots_with_instrument/', views.get_robots_with_instrument_data),
    path('robots/get_robot/<str:robot>/', views.get_robot),
    path('robots/delete_robot/', views.delete_robot),
    path('robots/calculate_robot_balance/', views.robot_balance_calc),
    path('robots/get_robot_balance/<str:env>/', views.get_robot_balances),
    path('robots/cumulative_ret/', views.cumulative_return),
    path('robots/pricing/', views.robot_pricing),
    path('robots/get_prices/', views.get_prices),
    path('robots/get_last_price/', views.get_last_price),
    path('robots/get/cash_flow/<str:robot>/', views.get_robot_cf),
    path('robots/update_strategy_params/', views.update_strategy_params),
]

urlpatterns = get_patterns + update_patterns + delete_patterns + \
              calculate_patterns + create_views + other_patterns
