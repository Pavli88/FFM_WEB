from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from portfolio.models import Portfolio, Transaction, TradeRoutes
from app_functions.request_functions import *
from django.db.models import Q
from accounts.models import BrokerAccounts
from instrument.models import Tickers


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
        request_data = json.loads(request.body.decode('utf-8'))

        try:
            transaction = Transaction.objects.get(id=request_data['id'])
            for key, value in request_data.items():
                setattr(transaction, key, value)
            transaction.save()
            return JsonResponse({'response': 'Transaction is updated'}, safe=False)
        except:
            return JsonResponse({'response': 'Error during update'}, safe=False)


@csrf_exempt
def update_trade_routing(request):
    if request.method == "POST":
        print('UPDATE TRADE ROUTING')
        request_body = json.loads(request.body.decode('utf-8'))
        print(request_body)
        trade_route = TradeRoutes.objects.get(id=request_body['id'])
        trade_route.is_active = request_body['is_active']
        trade_route.quantity = request_body['quantity']
        trade_route.broker_account_id = request_body['broker_account_id']
        trade_route.save()

        return JsonResponse({'response': 'Transaction is closed'}, safe=False)



