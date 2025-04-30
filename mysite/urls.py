from django.contrib import admin
from django.urls import path, include
from . import views, consumers
from mysite.views_folder import get_views, data_operations
from risk.views import *
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.conf.urls.static import static

create_patterns = [
    path('data/import/', data_operations.data_import),
]

general_patterns = [
    path('api/admin/', admin.site.urls),
    path('api/user/login/', views.login_user),
    path('api/user/logout/', views.logout_user),
    path('api/user/register/', views.register_user),
    path('api/user/forgot_password/', views.forgot_password),
    path('api/user/change_password/', views.change_password),
    path("api/user/change_email/", views.change_email),
    path('api/user/reset_password/<str:reset_token>/', views.reset_password),
    path('api/user/get/data/', views.get_user_data),
    path('api/upload_profile_picture/', views.upload_profile_picture),
    path('api/delete_profile_picture/', views.delete_profile_picture),
    path('api/update_user_profile/', views.update_user_profile),
    path('api/public_user_profile/<str:username>/', views.public_user_profile),
    path('api/follow/<str:username>/', views.follow_user),
    path('api/unfollow/<str:username>/', views.unfollow_user),
    path('api/check_following/<str:username>/', views.check_following),
    path("start-task/", start_task, name="start-task"),
    path("celery-status/", check_celery_status, name="celery-status"),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),  # Login
    path("api/token/refresh/", cookie_token_refresh, name="token_refresh"),
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

if settings.DEBUG:  # Only serve media files in development mode
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

