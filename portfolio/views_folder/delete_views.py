from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from portfolio.models import Transaction, TradeRoutes, PortGroup, Portfolio
import json
import pandas as pd
from calculations.processes.valuation.valuation import calculate_holdings


@csrf_exempt
def delete_transaction(request):
    if request.method == "POST":

        request_data = json.loads(request.body.decode('utf-8'))
        print("IDS",request_data['ids'])
        transaction = Transaction.objects.filter(id__in=request_data['ids'])
        # transaction_df = pd.DataFrame(transaction.values())
        # date = transaction_df['trade_date'].min()
        # portfolio_code = transaction_df['portfolio_code'][0]
        # print(date, portfolio_code)
        transaction.delete()
        # calculate_holdings(portfolio_code=portfolio_code, calc_date=date)
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

@csrf_exempt
def delete_portfolio(request):
    if request.method == "POST":
        print('DELETE PORTFOLIOS')
        request_data = json.loads(request.body.decode('utf-8'))
        print(request_data['ids'])
        # Portfolio.objects.get(id__in=request_data['ids']).delete()
        return JsonResponse({'message': 'Portfolio is deleted!', 'success': True}, safe=False)