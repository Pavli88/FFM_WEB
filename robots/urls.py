from django.urls import path
from . import views
from mysite.views import home

urlpatterns = [
    path('', home, name="home_page"),
    path('robots/', views.robots_main, name="robots main"),
    path('robots/trade_signals', views.execute_trade),
    path('robots/create_page', views.create_robot_page, name="go to create robot"),
    path('robots/create', views.create_robot, name="create robot"),
    path('robots/test_execution', views.test_execution, name="test execution"),
]
