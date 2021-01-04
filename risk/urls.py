from django.urls import path
from risk.views import *

urlpatterns = [
    path('risk/', risk_main, name="risk main template"),
]



