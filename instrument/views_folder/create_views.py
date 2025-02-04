import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from instrument.instrument_pricing.oanda_pricing import oanda_pricing
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
            price_list = request_body['data']
        except:
            price_list = [request_body]
        for price_record in price_list:
            print(price_record)
            try:
                price = Prices.objects.get(date=price_record['date'], instrument_id=int(price_record['instrument_id']))
                price.price = float(price_record['price'])
                price.save()
            except:
                Prices(date=price_record['date'],
                       instrument_id=int(price_record['instrument_id']),
                       price=float(price_record['price']),
                       source=price_record['source']).save()
        return JsonResponse({'response': 'Price inserted into database'}, safe=False)


@csrf_exempt
def instrument_pricing(request):
    if request.method == "POST":
        request_body = json.loads(request.body.decode('utf-8'))

        if request_body['broker'] == 'oanda':
            oanda_pricing(start_date=request_body['start_date'], end_date=request_body['end_date'])

        return JsonResponse('Pricing job has run', safe=False)