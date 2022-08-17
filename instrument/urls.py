from django.urls import path
from . import views
from signals.views import *

urlpatterns = [
    path('instruments/new/', views.new_instrument, name="new instrument"),
    path('instruments/get_instruments/', views.get_instruments),
    path('instruments/update_instrument/', views.update_instrument),
]