from django.urls import path
from . import views
from .views_folder import get_views, create_views, delete_views

create_patterns = [
    path('instruments/new/', create_views.new_instrument),
    path('instruments/new/ticker/', create_views.new_broker_ticker),
    path('instruments/new/price/', create_views.new_price),
    path('instruments/pricing/', create_views.instrument_pricing),
]

get_patterns = [
    path('instruments/get/instruments/', get_views.get_instruments),
    path('instruments/get/price/', get_views.get_prices),
    path('instruments/get/broker/tickers/', get_views.get_broker_tickers),
    path('users/search/', get_views.search_users),
    path('portfolios/search/', get_views.search_portfolios),

]

delete_patterns = [
    path('instruments/delete/broker/ticker/', delete_views.delete_broker_ticker),
    path('instruments/delete/price/', delete_views.delete_price),
]

other_patterns = [
    path('instruments/update_instrument/', views.update_instrument),
    path('instruments/delete_instrument/', views.delete_instrument),
]

urlpatterns = get_patterns + create_patterns + delete_patterns + other_patterns