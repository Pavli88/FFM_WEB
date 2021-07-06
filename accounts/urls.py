from django.urls import path
from accounts.views import *

urlpatterns = [
    path('accounts/create_account/', create_broker, name="create broker account"),
    path('accounts/new_cash_flow/', new_cash_flow),
    path('accounts/get_accounts/', new_cash_flow),
    path('accounts/get_accounts_data/', get_accounts_data),
    path('accounts/get_account_data/', get_account_data),
]