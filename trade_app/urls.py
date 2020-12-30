from django.urls import path
from trade_app.views import *

urlpatterns = [
    path('trade_page/', trade_main, name="trade_app main"),
    path('trade_page/submit_trade/', submit_trade, name="submit trade"),
    path('trade_page/load_trades/', get_open_trades),
    path('trade_page/close_trade/', close_trade),
]