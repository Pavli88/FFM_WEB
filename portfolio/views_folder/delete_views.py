from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from portfolio.models import Transaction, TradeRoutes, PortGroup
import json
import pandas as pd
from calculations.processes.valuation.valuation import calculate_holdings


@csrf_exempt
def delete_transaction(request):
    if request.method == "POST":
        request_data = json.loads(request.body.decode('utf-8'))
        transaction = Transaction.objects.get(id=request_data['id'])
        transaction.delete()
        calculate_holdings(portfolio_code=transaction.portfolio_code, calc_date=transaction.trade_date)
        return JsonResponse({'message': 'Transaction is deleted!', 'success': True}, safe=False)


@csrf_exempt
def delete_trade_routing(request):
    if request.method == "POST":
        request_data = json.loads(request.body.decode('utf-8'))
        TradeRoutes.objects.get(id=request_data['id']).delete()
        return JsonResponse({'response': 'Trade Routing is deleted!'}, safe=False)


@csrf_exempt
def delete_port_group(request):
    if request.method == "POST":
        print('DELETE NODE')
        request_data = json.loads(request.body.decode('utf-8'))
        PortGroup.objects.get(id=request_data['id']).delete()
        return JsonResponse({'message': 'Portfolio relationship is deleted!', 'success': True}, safe=False)