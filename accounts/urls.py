from django.urls import path
from accounts.views import *

urlpatterns = [
    path('accounts/get/brokers', get_brokers),
    path('accounts/credentials', broker_credentials),
    path('accounts/<int:pk>/update/', update_account),
    path('accounts/new_account/', new_account),
    path('accounts/new_broker/', new_broker),
    path('accounts/get/accounts/', get_accounts),
    path('accounts/delete/', delete_account),
    path('accounts/delete/broker/', delete_broker)
]