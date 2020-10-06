from django.urls import path
from . import views
from portfolio.views import *

urlpatterns = [
    path('portfolios/', portfolios_main, name="portfolio main"),
    path('portfolios/create/', create_portfolio, name="create portfolio"),
    path('portfolios/create/new_cash_flow/', new_cash_flow, name="create port cash flow"),
    path('portfolios/create/instrument/', create_instrument, name="create instrument"),
    path('portfolios/load_chart/', load_chart),
]