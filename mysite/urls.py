from django.contrib import admin
from django.urls import path, include
from . import views, consumers
from mysite.views_folder import get_views, data_operations
from risk.views import *
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

get_patterns = [
    path('exceptions/get/', views.get_exceptions),
]

create_patterns = [
    path('data/import/', data_operations.data_import),
]

general_patterns = [
    path('api/admin/', admin.site.urls),
    path('api/user/login/', views.login_user),
    path('api/user/logout/', views.logout_user),
    path('api/user/register/', views.register),
    path('api/user/change_password/', views.change_password),
    path('api/user/get/data/', views.get_user_data),
    path('exceptions/update/', views.update_exception_by_id),
    path("start-task/", start_task, name="start-task"),
    path("celery-status/", check_celery_status, name="celery-status"),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),  # Login
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),  # Refresh token
    path('api/', include('reports.urls')),
    path('api/', include('risk.urls')),
    path('api/', include('signals.urls')),
    path('api/', include('portfolio.urls')),
    path('api/', include('accounts.urls')),
    path('api/', include('trade_app.urls')),
    path('api/', include('instrument.urls')),
    path('api/', include('calculations.urls')),
]

urlpatterns = general_patterns + create_patterns

