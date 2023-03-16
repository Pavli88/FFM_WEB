from django.urls import path
from accounts.views import *

urlpatterns = [
    path('accounts/get/brokers', get_brokers),
    path('accounts/new_account/', create_broker),
    path('accounts/get_accounts/', get_accounts_data),
    path('accounts/get_account_data/', get_account_data),
    path('accounts/new_broker/', new_broker),
]