from django.urls import path
from . import views

urlpatterns = [
    path('incoming_signals/trade_signals', views.incoming_trade_signals)

]
