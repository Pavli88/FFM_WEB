from django.urls import path
from risk.views import *

get_patterns = [
    path('risk/get/robot/', robot_risk),
]

other_patterns = [
    path('risk/', risk_main, name="risk main template"),
    path('risk/update_robot_risk/', update_robot_risk),
    path('risk/get_robot_risk/<str:env>/', get_robot_risk),

]

urlpatterns = get_patterns + other_patterns



