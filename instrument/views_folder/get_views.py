from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from instrument.models import Instruments, Tickers
from app_functions.request_functions import *


@csrf_exempt
def get_instruments(request):
    if request.method == "POST":
        request_data = json.loads(request.body.decode('utf-8'))
        if request_data['name'] == '':
            instrument_name = ''
        else:
            instrument_name = request_data['name']
        filters = {}
        for key, value in request_data.items():
            if isinstance(value, list) and len(value) > 0:
                filters[key + '__in'] = value
            elif key == 'group':
                filters[key] = value
        return JsonResponse(list(Instruments.objects.filter(name__contains=instrument_name).filter(**filters).values()),
                            safe=False)


def get_instrument(request):
    if request.method == "GET":
        return JsonResponse(list(Instruments.objects.filter(id=request.GET.get('id')).values()), safe=False)


def get_broker_tickers(request):
    if request.method == "GET":
        return JsonResponse(dynamic_mode_get(request_object=request.GET.items(),
                                             column_list=['inst_code', 'source'],
                                             table=Tickers), safe=False)
