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
    print("")
    print("CASH HOLDING CALCULATION")
    body_data = json.loads(request.body.decode('utf-8'))
    start_date = datetime.datetime.strptime('2022-07-30', '%Y-%m-%d').date()
    end_date = datetime.datetime.strptime('2022-09-15', '%Y-%m-%d').date()
    portfolio_list = body_data['portfolio_list']
    print(start_date)
    print(end_date)
    print(portfolio_list)

    # if portfolio == "ALL":
    #     portfolio_list = Portfolio.objects.filter().values_list('portfolio_code', flat=True)
    # else:
    #     portfolio_list = [portfolio]
    # response_list = []
    for port in portfolio_list:
        print(port)
        port_data = Portfolio.objects.filter(portfolio_code=port).values()
        # inception_date = port_data[0]['inception_date']
        # if inception_date > start_date:
        #     return JsonResponse({'response': 'Portfolio inception date is greater than the calculation start date.'}, safe=False)

        cash_holding_calculation(portfolio_code='MAP_TEST', start_date=start_date, end_date=end_date)
        # while start_date <= end_date:
        #     cash_holding_calculation(portfolio_code=port, start_date=start_date)
        #     start_date = start_date + timedelta(days=1)
        #


    #     start_date = date
    #     responses = []
    #     if inception_date > start_date:
    #         print("    DATE:", start_date, )
    #         responses.append({'date': start_date.strftime('%Y-%m-%d'),
    #                           'msg': 'Calculation date is less than inception date.'})
    #     else:
    #         print("    DATE:", start_date)
    #         cash_holding(portfolio_code=port, start_date=start_date)
            # responses.append({'date': start_date.strftime('%Y-%m-%d'),
            #                   'msg': })
    return JsonResponse({'response': 'Process finished.'}, safe=False)


def get_cash_holding_history(request):
    if request.method == 'GET':
        start_date = datetime.datetime.strptime(request.GET.get('start_date'), '%Y-%m-%d').date()
        end_date = datetime.datetime.strptime(request.GET.get('end_date'), '%Y-%m-%d').date()
        portfolio_code = request.GET.get('portfolio_code')
        cash_history = cash_holding_calculation(portfolio_code=portfolio_code, start_date=start_date, end_date=end_date)
        return JsonResponse(list(cash_history.to_dict(orient='records')), safe=False)