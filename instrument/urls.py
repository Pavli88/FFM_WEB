from django.urls import path
from . import views
from instrument.instrument_prices import instrument_price_views
from .views_folder import get_views, create_views, delete_views

create_patterns = [
    path('instruments/new/', create_views.new_instrument),
    path('instruments/new/ticker/', create_views.new_broker_ticker),
]

get_patterns = [
    path('instruments/get/instruments/', get_views.get_instruments),
    path('instruments/get/broker/tickers/', get_views.get_broker_tickers),
]

delete_patterns = [
    path('instruments/delete/broker/ticker/', delete_views.delete_broker_ticker),
]

other_patterns = [
    path('instruments/new/price/', instrument_price_views.add_new_price),
    path('instruments/new/ticker/', instrument_price_views.add_new_ticker),
    path('instruments/get/prices/by_date', instrument_price_views.get_prices_for_security_by_date),
    path('instruments/get/tickers/', instrument_price_views.get_tickers_for_security),
    path('instruments/update_instrument/', views.update_instrument),
    path('instruments/delete_instrument/', views.delete_instrument),
]

urlpatterns = get_patterns + create_patterns + delete_patterns + other_patterns