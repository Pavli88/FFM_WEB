from django.urls import path
from . import views

urlpatterns = [
    path('reports/', views.report_main, name="reports main"),
]

