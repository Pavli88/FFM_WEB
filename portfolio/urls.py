from django.urls import path
from . import views
from portfolio.views import *

urlpatterns = [
    path('portfolios/', portfolios_main, name="portfolio main"),
    path('portfolios/create/', create_portfolio, name="create portfolio"),
    path('portfolios/create/new_cash_flow/', new_cash_flow, name="create port cash flow"),
    path('portfolios/sec_types/', get_securities_by_type),
    path('portfolios/trade_port/', trade, name="trade port"),
    path('portfolios/process_hub/', process_hub),
    path('portfolios/get_portfolio_data/', get_portfolio_data),
    path('portfolios/port_group/add/', add_port_to_group),
]