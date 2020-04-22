from django.urls import path
from . import views

urlpatterns = [
    path('risk/', views.risk_main, name="risk main template"),
    path('risk/get_balance/', views.get_balance, name="load account"),

]



