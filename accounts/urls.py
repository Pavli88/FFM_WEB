from django.urls import path
from accounts.views import *

urlpatterns = [
    path('accounts/get/brokers', get_brokers),
    path('accounts/new_account/', create_broker),
    path('accounts/get_account_data/', get_account_data),
    path('accounts/new_broker/', new_broker),
    path('accounts/get/accounts/', get_accounts),
    path('accounts/delete/', delete_account),
]