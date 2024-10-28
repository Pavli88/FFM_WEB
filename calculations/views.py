from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import datetime
from datetime import datetime
from mysite.my_functions.general_functions import *
from calculations.processes.performance.total_return import total_return_calc
from calculations.processes.valuation.valuation import calculate_holdings
from portfolio.models import Portfolio, TotalReturn
import pandas as pd
from mysite.signals import notification_signal
from mysite import consumers

@csrf_exempt
def valuation(request):
    if request.method == "POST":
        request_body = json.loads(request.body.decode('utf-8'))
        print(request_body)
        response_list = []
        for portfolio_code in request_body['portfolios']:
            responses = calculate_holdings(portfolio_code=portfolio_code, calc_date=request_body['start_date'])
            for resp in responses:
                response_list.append(resp)
        return JsonResponse(response_list, safe=False)


@csrf_exempt
def total_return(request):
    if request.method == "POST":
        request_body = json.loads(request.body.decode('utf-8'))
        print(request_body)
        response_list = []

        for portfolio_code in request_body['portfolios']:
            if request_body['calc_type'] == 'adhoc':
                print('adhoc')
                responses = total_return_calc(portfolio_code=portfolio_code,
                                              period='adhoc',
                                              end_date=request_body['end_date'],
                                              start_date=request_body['start_date']
                                              )
                for resp in responses:
                    response_list.append(resp)
            elif request_body['calc_type'] == 'multiple':
                print('multiple')
                for period in request_body['periods']:
                    responses = total_return_calc(portfolio_code=portfolio_code, period=period,
                                                  end_date=request_body['end_date'])
                    for resp in responses:
                        response_list.append(resp)
            else:
                print('multi dates')

        # # for portfolio_code in request_body['portfolios']:
        #     for period in request_body['periods']:
        #         responses = total_return_calc(portfolio_code=portfolio_code, period=period, end_date=request_body['date'])
        #         for resp in responses:
        #             response_list.append(resp)
        return JsonResponse(response_list, safe=False)
