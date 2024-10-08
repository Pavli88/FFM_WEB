from django.urls import path
from . import views
from portfolio.views import *
from portfolio.views_folder import create_views, get_views, update_view, delete_views, calculate_views

calculate_views = [
    path('portfolios/calculate/holding/', calculate_views.portfolio_holding),
]

create_views = [
    path('portfolios/new/trade_routing/', create_views.create_robot),
    path('portfolios/new/portfolio/', create_views.create_portfolio),
    path('portfolios/new/cashflow/', create_views.create_cashflow),
    path('portfolios/new/transaction/', create_views.new_transaction),
    path('portfolios/group/add/', create_views.add_to_portgroup),
]

get_views = [
    path('portfolios/get/exposures/', get_views.get_exposures),
    path('portfolios/get/nav/', get_views.get_nav),
    path('portfolios/get/total_pnl/', get_views.get_total_pnl),
    path('portfolios/get/monthly_pnl/', get_views.get_monthly_pnl),
    path('portfolios/get/portfolio_nav/', get_views.get_portfolio_nav),
    path('portfolios/get/grouped/portfolio_nav/', get_views.get_portfolio_nav_grouped),
    path('portfolios/get/drawdown/', get_views.get_drawdown),
    path('portfolios/get/cashflow/', get_views.daily_cashflow_by_type),
    path('portfolios/get/portfolios/', get_views.get_portfolios),
    path('portfolios/get/holding/', get_views.get_holding),
    path('portfolios/get/transactions/pnl/', get_views.transactions_pnls),
    path('portfolios/aggregated_pnl/', get_views.aggregated_security_pnl),
    path('portfolios/daily_cashflow/', get_views.daily_cashflow_by_type),
    path('portfolios/get/open_transactions/', get_views.get_open_transactions),
    path('portfolios/get/transactions/', get_views.get_portfolio_transactions),
    path('portfolios/get/perf_dashboard/', get_views.get_perf_dashboard),
    path('portfolios/get/trade_routes/', get_views.get_trade_routes),
    path('portfolios/get/historic_nav/', get_views.get_historic_nav),
    path('portfolios/get/port_groups/', get_views.get_port_groups),
]

update_views = [
    path('portfolios/update/portfolio/', update_view.update_portfolio),
    path('portfolios/update/transaction/', update_view.update_transaction),
    path('portfolios/update/trade_routing/', update_view.update_trade_routing),
]

delete_views = [
    path('portfolios/delete/transaction/', delete_views.delete_transaction),
    path('portfolios/delete/trade_routing/', delete_views.delete_trade_routing),
    path('portfolios/delete/port_group/', delete_views.delete_port_group),
]

other_patterns = [
    path('portfolios/get_portfolio_data/<str:portfolio>/', get_portfolio_data),
    path('portfolios/get_cash_flow/', get_cash_flow),
    path('portfolios/get_cash_holdings/', get_cash_holdings),
    path('portfolios/port_group/add/', add_port_to_group),
    path('portfolios/get_positions/', get_positions),
    path('portfolios/nav/<str:portfolio_code>', get_portfolio_nav),
    path('portfolios/import/<str:import_stream>', portfolio_import_stream),
]

urlpatterns = create_views + get_views + update_views + delete_views + calculate_views + other_patterns