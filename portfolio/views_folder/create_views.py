import pandas as pd
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from portfolio.models import TradeRoutes, PortGroup, Portfolio, Nav, Transaction
import json
from calculations.processes.valuation.valuation import calculate_holdings


@csrf_exempt
def create_robot(request):
    if request.method == "POST":
        request_data = json.loads(request.body.decode('utf-8'))
        if TradeRoutes.objects.filter(portfolio_code=request_data['portfolio_code'],
                                      inst_id=request_data['inst_id']).exists():
            return JsonResponse({'response': 'Security is already mapped to this portfolio'}, safe=False)
        else:
            TradeRoutes(portfolio_code=request_data['portfolio_code'],
                        inst_id=request_data['inst_id'],
                        ticker_id=request_data['ticker_id'],
                        broker_account_id=request_data['broker_account_id']).save()
            return JsonResponse({'response': 'Security mapping is completed'}, safe=False)


@csrf_exempt
def create_portfolio(request):
    if request.method == "POST":
        print('test')
        body_data = json.loads(request.body.decode('utf-8'))
        print(body_data)
        try:
            port = Portfolio(portfolio_name=body_data["port_name"],
                             portfolio_code=body_data["port_code"],
                             portfolio_type=body_data["port_type"],
                             currency=body_data["port_currency"],
                             inception_date=body_data["inception_date"],
                             owner=body_data["owner"])
            port.save()
            Nav(date=body_data["inception_date"], portfolio_code=body_data["port_code"]).save()

            return JsonResponse({'msg': "New Portfolio is created!", 'port': port.id}, safe=False)
        except:
            return JsonResponse({'msg': "Portfolio exists in database!", 'port': 0}, safe=False)
    return JsonResponse({'msg': "Invalid request method"}, status=405)


@csrf_exempt
def new_transaction(request):
    if request.method == "POST":
        request_body = json.loads(request.body.decode('utf-8'))

        print('NEW TRANSACTION')
        print(request_body)

        if 'initial_cash' in request_body:
            portfolio = Portfolio.objects.get(portfolio_code=request_body['portfolio_code'])
            portfolio.status = 'Funded'
            portfolio.save()
            del request_body['initial_cash']

        request_body['quantity'] = float(request_body['quantity']) if request_body['quantity'] else 0.0
        Transaction.objects.create(**request_body)
        calculate_holdings(portfolio_code=request_body['portfolio_code'], calc_date=request_body['trade_date'])
    return JsonResponse({"message": "Transaction is created!", 'success': True}, safe=False)


@csrf_exempt
def add_to_portgroup(request):
    if request.method == "POST":
        request_body = json.loads(request.body.decode('utf-8'))

        parent_id = request_body.get('parent_id')
        portfolio_id = request_body.get('portfolio_id')

        if PortGroup.objects.filter(parent_id=parent_id, portfolio_id=portfolio_id).exists():
            return JsonResponse({"message": "Portfolio is already assigned to a portfolio group"}, status=409)

        PortGroup.objects.create(parent_id=parent_id, portfolio_id=portfolio_id)

        return JsonResponse({"message": "Portfolio is added to the group", "success": True}, status=201)


