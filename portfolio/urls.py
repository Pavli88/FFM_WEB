from django.urls import path
from . import views
from portfolio.views import *
from portfolio.portfolio_queries.portfolio_cash.portfolio_cash_get import *
from portfolio.views_folder import create_views, get_views, update_view, delete_views, calculate_views

calculate_views = [
    path('portfolios/calculate/holding/', calculate_views.portfolio_holding),
]

create_views = [
    path('portfolios/create/robot/', create_views.create_robot),
    path('portfolios/new/portfolio/', create_views.create_portfolio),
    path('portfolios/new/cashflow/', create_views.create_cashflow),
    path('portfolios/new/transaction/', create_views.create_transaction),
    path('portfolios/calculate/cash_holding/', create_views.cash_holding_calculation),
    path('portfolios/calculate/nav/', create_views.cash_holding_calculation),

]

get_views = [
    path('portfolios/get/exposures/', get_views.get_exposures),
    path('portfolios/get/nav/', get_views.get_nav),
    path('portfolios/get/portfolio_nav/', get_views.get_portfolio_nav),
    path('portfolios/get/grouped/portfolio_nav/', get_views.get_portfolio_nav_grouped),
    path('portfolios/get/drawdown/', get_views.get_drawdown),
    path('portfolios/get/cashflow/', get_views.daily_cashflow_by_type),
    path('portfolios/get/portfolios/', get_views.get_portfolios),
    path('portfolios/get/holding/', get_views.get_holding),
    path('portfolios/get/transactions/pnl/', get_views.transactions_pnls),
    path('portfolios/aggregated_pnl/', get_views.aggregated_security_pnl),
    path('portfolios/daily_cashflow/', get_views.daily_cashflow_by_type),
    path('portfolios/available_cash/', get_views.available_cash),
    path('portfolios/get/open_transactions/', get_views.get_open_transactions),
    path('portfolios/get/transactions/', get_views.get_portfolio_transactions),
    path('portfolios/get/main_portfolio_cashflow/', get_views.get_main_portfolio_cashflows),
]

update_views = [
    path('portfolios/update/portfolio/', update_view.update_portfolio),
    path('portfolios/update/transaction/', update_view.update_transaction),
]

delete_views = [
    path('portfolios/delete/transaction/', delete_views.delete_transaction),
]

other_patterns = [
    path('portfolios/new_cash_flow/', new_cash_flow),
    path('portfolios/new_transaction/', new_transaction),
    path('portfolios/get_portfolio_data/<str:portfolio>/', get_portfolio_data),
    path('portfolios/get_cash_flow/', get_cash_flow),
    path('portfolios/get_cash_holdings/', get_cash_holdings),
    path('portfolios/port_group/add/', add_port_to_group),
    path('portfolios/positions/', pos_calc),
    path('portfolios/calculate/cash_holding/', cash_calc),
    path('portfolios/holdings_calc/', holdings_calc),
    path('portfolios/get_positions/', get_positions),
    path('portfolios/nav/<str:portfolio_code>', get_portfolio_nav),
    path('portfolios/import/<str:import_stream>', portfolio_import_stream),
    path('portfolios/cash/total/by_type/<str:portfolio_code>', get_port_total_cash_by_type),
    path('portfolios/cash/holding/<str:date>', get_cash_holding_by_date),
]

urlpatterns = create_views + get_views + update_views + delete_views + calculate_views + other_patterns