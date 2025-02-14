from django.contrib import admin
from django.urls import path, include

from . import views, consumers
from mysite.views_folder import get_views, data_operations
from risk.views import *

get_patterns = [
    path('exceptions/get/', views.get_exceptions),
]

create_patterns = [
    path('data/import/', data_operations.data_import),
]

general_patterns = [
    path('', views.main_page_react),
    path('user_login/', views.login_user),
    path('user_logout/', views.logout_user),
    path('user_register/', views.register),
    path('admin/', admin.site.urls),
    path('', include('reports.urls')),
    path('', include('risk.urls')),
    path('', include('signals.urls')),
    path('', include('portfolio.urls')),
    path('', include('accounts.urls')),
    path('', include('trade_app.urls')),
    path('', include('instrument.urls')),
    path('', include('calculations.urls')),
    path('home/system_messages/<str:type>/', system_messages),
    path('home/verify_sys_msg/<str:msg_id>/', verify_system_message),
    path('exceptions/update/', views.update_exception_by_id)
]

urlpatterns = get_patterns + general_patterns + create_patterns

