from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import datetime
from datetime import datetime
from mysite.my_functions.general_functions import *
from app_functions.calculations import *
from portfolio.models import Portfolio
import pandas as pd


@csrf_exempt
def valuation(request):
    if request.method == "POST":
        request_body = json.loads(request.body.decode('utf-8'))
        print(request_body)
        response_list = []
        for portfolio_code in request_body['portfolios']:
            responses = calculate_holdings(portfolio_code=portfolio_code, calc_date=request_body['date'])
            for resp in responses:
                response_list.append(resp)
        return JsonResponse(response_list, safe=False)


