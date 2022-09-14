from django.urls import path
from . import views
from portfolio.views import *
from portfolio.portfolio_queries.portfolio_cash.portfolio_cash_get import *

urlpatterns = [
    path('portfolios/new/', create_portfolio),
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
    path('portfolios/get_portfolio_transactions/<str:portfolio>/', get_port_transactions),
    path('portfolios/import/<str:import_stream>', portfolio_import_stream),
    path('portfolios/cash/total/by_type/<str:portfolio_code>', get_port_total_cash_by_type),
    path('portfolios/cash/holding/<str:date>', get_cash_holding_by_date),
]