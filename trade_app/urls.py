from django.urls import path
from trade_app.views import *
from .views_folder import get_views, update_views, create_view, delete_views

get_patterns = [
    path('trade_page/get/open_trades/<str:environment>/', get_views.get_open_trades),
    path('trade_page/notifications/trade_signals/', get_views.trade_signals),
]

create_view = [
    path('trade_page/new/signal/', create_view.new_transaction_signal),
]

update_views = [
    path('trade_page/portfolio/close_transaction/', update_views.close_transaction),
]

delete_views = [
    path('trade_page/delete/signals/', delete_views.delete_notifications),
]

other_patterns = [
    path('trade_page/trade/new/', new_trade),
    path('trade_page/get_open_trades/<str:env>/', get_open_trades),
    path('trade_page/open_trades/<str:robot>/', get_open_trades_robot),
    path('trade_page/close_trade/', close_trade),
    path('trade_page/trade/signal_execution/', trade_execution),
    path('trade_page/edit_transaction/', edit_transaction),
]

urlpatterns = get_patterns + update_views + create_view + delete_views + other_patterns