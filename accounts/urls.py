from django.urls import path
from accounts.views import *

urlpatterns = [
    path('accounts/', accounts_main, name="accounts main"),
    path('accounts/get_accounts/', get_all_accounts, name="show accounts"),
    path('accounts/create_account/', create_broker, name="create broker account"),
]