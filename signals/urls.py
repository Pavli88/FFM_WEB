from django.urls import path
from signals.views import *

# This url site will be responsible for handling incoming signals
# Signals can be trade signals, or any kind of data feeds that arrive to ffm system

urlpatterns = [
    path('trade/', incoming_trade, name="test_execution"),
]
