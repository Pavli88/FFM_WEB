from django.urls import path
from accounts.views import *

urlpatterns = [
    path('accounts/new_account/', create_broker),
    path('accounts/get_accounts_data/', get_accounts_data),
    path('accounts/get_account_data/', get_account_data),
]