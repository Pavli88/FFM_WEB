from django.urls import path
from .views import *

urlpatterns = [
    path('calculate/portfolio/cash_holding/', portfolio_cash_holding_calc),
    path('calculate/get/portfolio/processes/', get_portfolio_process_statuses),
]