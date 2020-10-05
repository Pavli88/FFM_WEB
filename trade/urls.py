from django.urls import path
from trade.views import *

urlpatterns = [
    path('trade_page/', trade_main, name="trade main"),
]