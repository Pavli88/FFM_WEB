from django.urls import path
from . import views
from signals.views import *

urlpatterns = [
    path('robots/', views.robots_main, name="robots main"),
    path('robots/create', views.create_robot, name="create robot"),
    path('robots/get_robots', views.get_all_robots, name="show robots"),
    path('robots/amend_robot', views.amend_robot, name="amend robot"),
]
