from django.urls import path
from . import views
from signals.views import *

urlpatterns = [
    path('instruments/', views.instruments_main, name="instruments main"),
    path('instruments/new/', views.new_instrument, name="new instrument"),
    path('instruments/get/', views.get_instruments),
]