from django.urls import path
from signals.views import *

urlpatterns = [
    path('signals/trade/', incoming_trade),
]
