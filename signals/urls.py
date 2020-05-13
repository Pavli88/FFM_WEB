from django.urls import path
from signals.views import *

# This url site will be responsible for handling incoming signals
# Signals can be trade signals, or any kind of data feeds that arrive to ffm system

urlpatterns = [
    path('new_trade/', new_execution, name="test_execution"),
    path('close_trade/', close_all_trades, name="test_close_execution"),
]
