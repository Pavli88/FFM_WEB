from django.urls import path
from . import views
from portfolio.views import *
from portfolio.views_folder import create_views, get_views, update_view, delete_views, calculate_views

calculate_views = [

]

create_views = [
    path('portfolios/new/trade_routing/', create_views.create_trade_routing),
    path('portfolios/new/portfolio/', create_views.create_portfolio),
    path('portfolios/new/transaction/', create_views.new_transaction),
    path('portfolios/group/add/', create_views.add_to_portgroup),
]

get_views = [
    path('portfolios/get/exposures/', get_views.get_exposures),
    path('portfolios/get/nav/', get_views.get_nav),
    path('portfolios/get/total_returns/', get_views.get_total_returns),
    path('portfolios/get/drawdown/', get_views.get_drawdown),
    path('portfolios/get/portfolios/', get_views.get_portfolios),
    path('portfolios/get/holding/', get_views.get_holding),
    path('portfolios/get/open_transactions/', get_views.get_open_transactions),
    path('portfolios/get/transactions/', get_views.get_portfolio_transactions),
    path('portfolios/get/trade_routes/', get_views.get_trade_routes),
    path('portfolios/get/port_groups/', get_views.get_port_groups),
    path('portfolios/get/position_exposures/', get_views.get_position_exposures),
    path('portfolios/group/<str:portfolio_code>/', get_views.get_child_portfolios),
]

update_views = [
    path('portfolios/update/portfolio/', update_view.update_portfolio),
    path('portfolios/update/transaction/', update_view.update_transaction),
    path('portfolios/update/trade_routing/', update_view.update_trade_routing),
]

delete_views = [
    path('portfolios/delete/transaction/', delete_views.delete_transaction),
    path('portfolios/delete/trade_routing/', delete_views.delete_trade_routing),
    path('portfolios/delete/port_group/', delete_views.delete_port_group),
    path('portfolios/delete/portfolios/', delete_views.delete_portfolios),
]

other_patterns = [
    path('portfolios/get_portfolio_data/<str:portfolio>/', get_portfolio_data),
    path('portfolios/port_group/add/', add_port_to_group),
    path('portfolios/nav/<str:portfolio_code>', get_portfolio_nav),
    path('portfolios/import/<str:import_stream>', portfolio_import_stream),
]

urlpatterns = create_views + get_views + update_views + delete_views + calculate_views + other_patterns