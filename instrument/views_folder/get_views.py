import pandas as pd
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from instrument.models import Instruments, Tickers, Prices
from app_functions.request_functions import *


@csrf_exempt
def get_instruments(request):
    if request.method == "POST":
        request_data = json.loads(request.body.decode('utf-8'))
        print(request_data)
        # if request_data['name'] == '':
        #     instrument_name = ''
        # else:
        #     instrument_name = request_data['name']
        # filters = {}
        # for key, value in request_data.items():
        #     if isinstance(value, list) and len(value) > 0:
        #         filters[key + '__in'] = value
        #     elif key == 'group':
        #         filters[key] = value

        results = dynamic_mode_get(request_object=request_data.items(),
                                   column_list=['name', 'group', 'group__in', 'type__in', 'country__in', 'cash', 'currency', 'currency__in'],
                                   table=Instruments)
        print(results)
        # Instruments.objects.filter(name__contains=instrument_name).filter(**filters).values()
        return JsonResponse(list(results), safe=False)


def get_instrument(request):
    if request.method == "GET":
        return JsonResponse(list(Instruments.objects.filter(id=request.GET.get('id')).values()), safe=False)


def get_broker_tickers(request):
    if request.method == "GET":
        return JsonResponse(dynamic_mode_get(request_object=request.GET.items(),
                                             column_list=['inst_code', 'source'],
                                             table=Tickers), safe=False)


def get_prices(request):
    if request.method == "GET":
        prices = dynamic_mode_get(request_object=request.GET.items(),
                                  column_list=['inst_code', 'date', 'date__gte', 'date__lte'],
                                  table=Prices)
        print(len(prices))
        if len(prices) == 0:
            return JsonResponse(list({}), safe=False)
        else:
            print(pd.DataFrame(prices).sort_values('date').to_dict('records'))
            return JsonResponse(pd.DataFrame(prices).sort_values('date').to_dict('records'), safe=False)
