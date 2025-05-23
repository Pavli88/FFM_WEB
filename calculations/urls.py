from django.urls import path
from .views import *

urlpatterns = [
    path('calculate/valuation/', valuation),
    path('calculate/total_return/', total_return),
    path('calculate/audit_records/', audit_records),
    path('calculate/exceptions/', get_exceptions_by_audit_ids, name='get_exceptions_by_audit_ids'),
]