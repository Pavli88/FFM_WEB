import json
import pandas as pd
from portfolio.models import Transaction
from instrument.models import Prices
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from instrument.instrument_pricing.oanda_pricing import oanda_pricing
from instrument.models import *
import csv


@csrf_exempt
def data_import(request):
    if request.method == "POST":
        print('DATA IMPORT')
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file provided'})

        file = pd.read_csv(request.FILES['file'])
        process = request.POST.get('process')

        print(process)

        if process == 'transaction':
            transaction_import(file=file)
            print(file)
            return JsonResponse({'success': True})

        response = {'response': 'Data is loaded'}
        return JsonResponse(response, safe=False)


def transaction_import(file):
    print('TRANSACTION IMPORT')

def price_import():
    print('PRICE IMPORT')

def fx_import():
    print('FX IMPORT')

def instrument_import():
    print('INSTRUMENT IMPORT')

def nav_import():
    print('NAV IMPORT')