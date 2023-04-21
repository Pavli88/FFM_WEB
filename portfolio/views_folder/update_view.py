from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from portfolio.models import Portfolio, Transaction
from app_functions.request_functions import *


@csrf_exempt
def update_portfolio(request):
    if request.method == "POST":
        print('PORTFOLIO UPDATE')
        request_data = json.loads(request.body.decode('utf-8'))
        print(request_data)
        try:
            portfolio = Portfolio.objects.get(id=request_data['id'])
            for key, value in request_data.items():
                setattr(portfolio, key, value)
            portfolio.save()
            return JsonResponse({'response': 'Portfolio is updated'}, safe=False)
        except:
            return JsonResponse({'response': 'Error during update'}, safe=False)


@csrf_exempt
def update_transaction(request):
    if request.method == "POST":
        dynamic_model_update(table_object=Transaction,
                             request_object=json.loads(request.body.decode('utf-8')))
        return JsonResponse({'response': 'Transaction is updated'}, safe=False)



