from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name="home_page"),
    path('admin/', admin.site.urls),
    path('', include('reports.urls')),
    path('', include('robots.urls')),
    path('', include('risk.urls')),
    path('', include('signals.urls')),
    path('', include('portfolio.urls')),
    path('', include('accounts.urls')),
    path('', include('trade.urls')),
    path('trade_results/', views.get_results, name="get_results"),
    path('save_home/', views.save_layout, name="make_default"),
    path('settings/', views.go_to_settings, name="settings main"),
    path('settings/save/', views.save_settings, name="save settings"),
    path('switch_account/', views.switch_account),

]
