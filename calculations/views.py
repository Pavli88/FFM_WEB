from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

import json
import datetime
from datetime import datetime

from mysite.my_functions.general_functions import *

# Process imports
from calculations.processes.portfolio.cash_holding_calculation import cash_holding_calculation

# Model imports
from .models import PortfolioProcessStatus
from portfolio.models import Portfolio


def get_portfolio_process_statuses(request):
    if request.method == 'GET':
        return JsonResponse(list(PortfolioProcessStatus.objects.filter(date__gte=request.GET.get('start_date'),
                                                                       portfolio_code=request.GET.get(
                                                                           'portfolio_code')).values()), safe=False)


@csrf_exempt
def portfolio_cash_holding_calc(request):
    if request.method == 'GET':
        print("")
        print("CASH HOLDING CALCULATION")
        start_date = datetime.datetime.strptime(request.GET.get('start_date'), '%Y-%m-%d').date()
        end_date = datetime.datetime.strptime(request.GET.get('end_date'), '%Y-%m-%d').date()
        portfolio_list = request.GET.get('portfolio_list')
        print(start_date)
        print(end_date)
        print(portfolio_list)

        # if portfolio == "ALL":
        #     portfolio_list = Portfolio.objects.filter().values_list('portfolio_code', flat=True)
        # else:
        #     portfolio_list = [portfolio]
        # response_list = []
        for port in portfolio_list:
            cash_holding_calculation(portfolio_code=port, start_date=start_date, end_date=end_date)
        return JsonResponse({'response': 'Process finished.'}, safe=False)


def get_cash_holding_history(request):
    if request.method == 'GET':
        start_date = datetime.datetime.strptime(request.GET.get('start_date'), '%Y-%m-%d').date()
        end_date = datetime.datetime.strptime(request.GET.get('end_date'), '%Y-%m-%d').date()
        portfolio_code = request.GET.get('portfolio_code')
        cash_history = cash_holding_calculation(portfolio_code=portfolio_code, start_date=start_date, end_date=end_date)
        return JsonResponse(list(cash_history.to_dict(orient='records')), safe=False)