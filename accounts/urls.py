from django.urls import path
from accounts.views import *

urlpatterns = [
    path('accounts/', accounts_main, name="accounts main"),
    path('accounts/create_broker/', create_broker, name="create broker account"),
]