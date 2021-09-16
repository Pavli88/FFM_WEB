from django.urls import path
from trade_app.views import *

urlpatterns = [
    path('trade_page/submit_trade/', submit_trade, name="submit trade"),
    path('trade_page/get_open_trades/<str:env>/', get_open_trades),
    path('trade_page/close_trade/', close_trade),
    path('trade_page/close_trade/test/', close_trade_test),
]