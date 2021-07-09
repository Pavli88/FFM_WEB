from django.urls import path
from . import views
from portfolio.views import *

urlpatterns = [
    path('portfolios/new/', create_portfolio),
    path('portfolios/new_cash_flow/', new_cash_flow),
    path('portfolios/portfolio_trade/', portfolio_trade),
    path('portfolios/get_portfolio_data/', get_portfolio_data),
    path('portfolios/port_group/add/', add_port_to_group),
    path('portfolios/positions/', pos_calc),
    path('portfolios/cash_holding/', cash_calc),
    path('portfolios/get_portfolio_transactions/<str:portfolio>/', get_port_transactions),
]