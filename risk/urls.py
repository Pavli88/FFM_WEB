from django.urls import path
from risk.views import *

urlpatterns = [
    path('risk/', risk_main, name="risk main template"),
    path('risk/get_balance/', get_balance, name="load account"),
    path('risk/save_account/', save_account_risk, name="save_account_risk"),
    path('risk/save_robot/', save_robot_risk, name="save_robot_risk"),

]



