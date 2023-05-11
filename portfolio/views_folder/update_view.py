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
        request_body = json.loads(request.body.decode('utf-8'))
        print(request_body)
        dynamic_model_update(table_object=Transaction,
                             request_object=request_body)
        related_transactions = Transaction.objects.filter(transaction_link_code=int(request_body['id'])).filter(Q(sec_group='Cash') | Q(sec_group='Margin')).values()
        for transaction in related_transactions:
            print(transaction)
            if transaction['margin'] > 0.0:
                transaction['quantity'] = float(request_body['quantity']) * float(request_body['price']) * float(transaction['margin'])
            else:
                transaction['quantity'] = float(request_body['quantity']) * float(request_body['price'])
            dynamic_model_update(table_object=Transaction,
                                 request_object=transaction)

        calculate_cash_holding(portfolio_code=request_body['portfolio_code'],
                               start_date=request_body['trade_date'],
                               currency=request_body['currency'])

        return JsonResponse({'response': 'Transaction is updated'}, safe=False)



