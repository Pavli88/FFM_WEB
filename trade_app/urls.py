from django.urls import path
from trade_app.views import *

urlpatterns = [
    path('trade_page/trade/new/', new_trade),
    path('trade_page/get_open_trades/<str:env>/', get_open_trades),
    path('trade_page/open_trades/<str:robot>/', get_open_trades_robot),
    path('trade_page/close_trade/', close_trade),
    path('trade_page/trade/signal_execution/', trade_execution),
    path('trade_page/edit_transaction/', edit_transaction),
]