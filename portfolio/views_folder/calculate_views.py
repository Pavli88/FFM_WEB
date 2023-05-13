from django.views.decorators.csrf import csrf_exempt
import pandas as pd
from django.http import JsonResponse
import json
from app_functions.calculations import *


@csrf_exempt
def portfolio_holding(request):
    if request.method == "POST":
        print('Portfolio Holding Calc')
        calculate_holdings(portfolio_code='TST', calc_date='2023-05-01')

        # Query latest holdings data

        return JsonResponse({'response': 'Portfolio Holding'}, safe=False)