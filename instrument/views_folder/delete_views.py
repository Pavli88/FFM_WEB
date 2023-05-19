import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from instrument.models import *


@csrf_exempt
def delete_broker_ticker(request):
    if request.method == "POST":
        request_data = json.loads(request.body.decode('utf-8'))
        Tickers.objects.get(id=request_data['id']).delete()
        response = 'Ticker deleted!'
        return JsonResponse(response, safe=False)


@csrf_exempt
def delete_price(request):
    if request.method == "POST":
        request_data = json.loads(request.body.decode('utf-8'))
        Prices.objects.get(id=request_data['id']).delete()
        return JsonResponse({'response': 'Price is deleted'}, safe=False)