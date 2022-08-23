from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from instrument.models import *


@csrf_exempt
def add_new_price(request):
    if request.method == "POST":
        request_data = json.loads(request.body.decode('utf-8'))
        try:
            price_record = Prices.objects.get(inst_code=request_data['inst_code'],
                                              date=request_data['date'],
                                              source=request_data['source'])
            price_record.price = request_data['price']
            price_record.save()
        except Prices.DoesNotExist:
            print('price does not exist')
            Prices(inst_code=request_data['inst_code'],
                   date=request_data['date'],
                   price=request_data['price'],
                   source=request_data['source']).save()
        response = ""
        return JsonResponse(response, safe=False)


def get_prices_for_security_by_date(request):
    if request.method == "GET":
        prices = Prices.objects.filter(inst_code=request.GET.get('inst_code'),
                                    date=request.GET.get('date')).values()
        print(prices)
        return JsonResponse(list(prices), safe=False)