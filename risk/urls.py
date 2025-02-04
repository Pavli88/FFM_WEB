from django.urls import path
from risk.views import *

get_patterns = [

]

other_patterns = [
    path('risk/', risk_main, name="risk main template"),
]

urlpatterns = get_patterns + other_patterns



