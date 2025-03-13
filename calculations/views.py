from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from mysite.my_functions.general_functions import *
from calculations.processes.performance.total_return import total_return_calc
from calculations.processes.valuation.valuation import calculate_holdings
from datetime import datetime, timedelta

@csrf_exempt
def valuation(request):
    if request.method == "POST":
        request_body = json.loads(request.body.decode('utf-8'))
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
                start_date = datetime.strptime(request_body['start_date'], "%Y-%m-%d")
                end_date = datetime.strptime(request_body['end_date'], "%Y-%m-%d")
                for period in request_body['periods']:
                    current_date = start_date
                    while current_date <= end_date:
                        responses = total_return_calc(portfolio_code=portfolio_code,
                                                      period=period,
                                                      end_date=current_date.strftime("%Y-%m-%d"))
                        for resp in responses:
                            response_list.append(resp)
                        current_date += timedelta(days=1)
                        #
        # # for portfolio_code in request_body['portfolios']:
        #     for period in request_body['periods']:
        #         responses = total_return_calc(portfolio_code=portfolio_code, period=period, end_date=request_body['date'])
        #         for resp in responses:
        #             response_list.append(resp)
        return JsonResponse(response_list, safe=False)
