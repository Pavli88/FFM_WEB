import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Model Imports
from instrument.models import *


@csrf_exempt
def new_instrument(request):
    if request.method == "POST":
        request_data = json.loads(request.body.decode('utf-8'))
        column_names = [field.name for field in Instruments._meta.fields]
        try:
            Instruments(name=request_data['name'],
                        code=request_data['code'],
                        ticker=request_data['ticker'],
                        country=request_data['country'],
                        group=request_data['group'],
                        type=request_data['type'],
                        currency=request_data['currency'],
                        ).save()
            response = 'Instrument is Saved!'
        except:
            response = 'Instrument code already exists!'

        # except:
        #     response = 'Instrument Internal Code Exists in Database!'
        return JsonResponse(response, safe=False)


@csrf_exempt
def new_broker_ticker(request):
    if request.method == "POST":
        request_data = json.loads(request.body.decode('utf-8'))
        ticker_assigned = Tickers.objects.filter(inst_code=request_data['inst_code'], source=request_data['source']).exists()
        if ticker_assigned:
            return JsonResponse('Ticker has already been assigned to this security at this broker!', safe=False)
        try:
            Tickers(
                inst_code=request_data['inst_code'],
                source=request_data['source'],
                source_ticker=request_data['source_ticker'],
                margin=request_data['margin']
            ).save()
            response = 'Broker ticker is saved!'
        except:
            response = 'Broker ticker already exists!'

        return JsonResponse(response, safe=False)