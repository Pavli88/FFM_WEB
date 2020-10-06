from django.urls import path
from trade_app.views import *

urlpatterns = [
    path('trade_page/', trade_main, name="trade_app main"),
]