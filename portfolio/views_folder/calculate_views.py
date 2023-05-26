from django.views.decorators.csrf import csrf_exempt
import pandas as pd
from django.http import JsonResponse
import json
from app_functions.calculations import *
from datetime import date
from datetime import datetime


@csrf_exempt
def portfolio_holding(request):
    if request.method == "POST":
        request_body = json.loads(request.body.decode('utf-8'))
        response = calculate_holdings(portfolio_code=request_body['portfolio_code'], calc_date=request_body['start_date'])
        return JsonResponse({'response': response}, safe=False)