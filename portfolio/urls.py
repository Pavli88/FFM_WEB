from django.urls import path
from . import views
from portfolio.views import *

urlpatterns = [
    path('portfolios/', portfolios_main, name="portfolio main"),
    path('portfolios/create/', create_portfolio, name="create portfolio"),

]