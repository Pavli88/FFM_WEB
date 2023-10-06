from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from portfolio.models import Portfolio, Transaction
from app_functions.request_functions import *
from app_functions.calculations import calculate_cash_holding
from django.db.models import Q


@csrf_exempt
def update_portfolio(request):
    if request.method == "POST":
        request_data = json.loads(request.body.decode('utf-8'))

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
        request_body = json.loads(request.body.decode('utf-8'))

        if request_body['transaction_link_code'] != 0:
            main_transaction = Transaction.objects.get(id=request_body['transaction_link_code'])
            request_body['realized_pnl'] = float(request_body['quantity']) * (
                    float(request_body['price']) - float(main_transaction.price))

        request_body['mv'] = round(float(request_body['quantity']) * float(request_body['price']) * float(request_body['fx_rate']), 5)
        request_body['local_mv'] = round(float(request_body['quantity']) * float(request_body['price']), 5)
        dynamic_model_update(table_object=Transaction,
                             request_object=request_body)

        return JsonResponse({'response': 'Transaction is updated'}, safe=False)



