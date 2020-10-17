from django.urls import path
from . import views
from signals.views import *

urlpatterns = [
    path('instruments/', views.instruments_main, name="instruments main"),
]