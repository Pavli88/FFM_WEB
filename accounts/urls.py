from django.urls import path
from accounts.views import *

urlpatterns = [
    path('accounts/', accounts_main, name="accounts main"),
    path('accounts/create_account/', create_broker, name="create broker account"),
    path('accounts/load_accounts/', load_accounts),
    path('accounts/new_cash_flow/', new_cash_flow),
    path('accounts/get_accounts/', new_cash_flow),
]