from django.urls import path
from accounts.views import *

urlpatterns = [
    path('accounts/', accounts_main, name="accounts main"),
]