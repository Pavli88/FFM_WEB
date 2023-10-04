from django.urls import path
from .views import *

urlpatterns = [
    path('calculate/valuation/', valuation),
    path('calculate/total_return/', total_return),
]