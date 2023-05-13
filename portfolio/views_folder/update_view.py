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

        if request_body['transaction_link_code'] != '':
            main_transaction = Transaction.objects.get(id=request_body['transaction_link_code'])
            # request_body['outstanding_units'] = main_transaction.quantity - request_body['quantity']
            request_body['realized_pnl'] = float(request_body['quantity']) * (
                    float(request_body['price']) - float(main_transaction.price))

        dynamic_model_update(table_object=Transaction,
                             request_object=request_body)
        # calculate_cash_holding(portfolio_code=request_body['portfolio_code'],
        #                        start_date=request_body['trade_date'],
        #                        currency=request_body['currency'])

        return JsonResponse({'response': 'Transaction is updated'}, safe=False)



