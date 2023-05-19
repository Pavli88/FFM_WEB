import json
from instrument.models import Prices
from app_functions.request_functions import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Model Imports
from instrument.models import *


@csrf_exempt
def new_instrument(request):
    if request.method == "POST":
        request_data = json.loads(request.body.decode('utf-8'))
        try:
            Instruments(name=request_data['name'],
                        country=request_data['country'],
                        group=request_data['group'],
                        type=request_data['type'],
                        currency=request_data['currency'],
                        ).save()
            response = 'Instrument is Saved!'
        except:
            response = 'Error occured during saving the instrument!'
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


@csrf_exempt
def new_price(request):
    if request.method == "POST":
        request_body = json.loads(request.body.decode('utf-8'))
        try:
            price = Prices.objects.get(date=request_body['date'], inst_code=request_body['inst_code'])
            price.price = request_body['price']
            price.save()
        except:
            Prices(date=request_body['date'],
                   inst_code=request_body['inst_code'],
                   price=request_body['price']).save()
        return JsonResponse({'response': 'Price inserted to db'}, safe=False)