import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Model Imports
from instrument.models import *


@csrf_exempt
def delete_broker_ticker(request):
    if request.method == "POST":
        request_data = json.loads(request.body.decode('utf-8'))
        Tickers.objects.get(id=request_data['id']).delete()
        response = 'Ticker deleted!'
        return JsonResponse(response, safe=False)