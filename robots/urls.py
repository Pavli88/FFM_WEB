from django.urls import path
from . import views

urlpatterns = [
    path('robots/', views.robots_main, name="robots main"),
    path('robots/trade_signals', views.execute_trade),
    path('robots/create', views.create_robot, name="create robot"),
    path('robots/test_execution', views.test_execution, name="test execution"),
    path('robots/get_robots', views.get_robots, name="get robots"),
]
