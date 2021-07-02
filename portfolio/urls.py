from django.urls import path
from . import views
from portfolio.views import *

urlpatterns = [
    path('portfolios/new/', create_portfolio),
    path('portfolios/new_cash_flow/', new_cash_flow, name="create port cash flow"),
    path('portfolios/trade_port/', trade, name="trade port"),
    path('portfolios/process_hub/', process_hub),
    path('portfolios/get_portfolio_data/', get_portfolio_data),
    path('portfolios/port_group/add/', add_port_to_group),
]