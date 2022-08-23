from django.urls import path
from . import views
from instrument.instrument_prices import instrument_price_views
from signals.views import *

urlpatterns = [
    path('instruments/new/', views.new_instrument, name="new instrument"),
    path('instruments/new/price/', instrument_price_views.add_new_price),
    path('instruments/get_instruments/', views.get_instruments),
    path('instruments/get/prices/by_date', instrument_price_views.get_prices_for_security_by_date),
    path('instruments/update_instrument/', views.update_instrument),
    path('instruments/delete_instrument/', views.delete_instrument),
]
