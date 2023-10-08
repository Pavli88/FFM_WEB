import pandas as pd
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from portfolio.models import Robots, Portfolio, Transaction
from instrument.models import Instruments, Tickers, Prices
from accounts.models import BrokerAccounts
import json
from app_functions.request_functions import *
from app_functions.calculations import *
from calculations.processes.valuation.valuation import calculate_holdings


@csrf_exempt
def create_robot(request):
    if request.method == "POST":
        request_data = json.loads(request.body.decode('utf-8'))
        if Robots.objects.filter(portfolio_code=request_data['portfolio_code'],
                                 inst_id=request_data['inst_id']).exists():
            return JsonResponse({'response': 'Security is already mapped to this portfolio'}, safe=False)
        else:
            Robots(portfolio_code=request_data['portfolio_code'],
                   inst_id=request_data['inst_id'],
                   ticker_id=request_data['ticker_id'],
                   broker_account_id=request_data['broker_account_id']).save()
            return JsonResponse({'response': 'Security mapping is completed'}, safe=False)


@csrf_exempt
def create_portfolio(request):
    if request.method == "POST":
        body_data = json.loads(request.body.decode('utf-8'))
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


@csrf_exempt
def create_cashflow(request):
    if request.method == "POST":
        request_body = json.loads(request.body.decode('utf-8'))
        Transaction(
            portfolio_code=request_body['portfolio_code'],
            security=request_body['security'],
            transaction_type=request_body['transaction_type'],
            trade_date=request_body['trade_date'],
            quantity=float(request_body['quantity']),
            currency=request_body['currency']
        ).save_cashflow()
        calculate_holdings(portfolio_code=request_body['portfolio_code'], calc_date=request_body['trade_date'])
        return JsonResponse({"msg": "Cashflow entered into database!"}, safe=False)


@csrf_exempt
def save_transaction(request):
    if request.method == "POST":
        request_body = json.loads(request.body.decode('utf-8'))
        print(request_body)
        account = BrokerAccounts.objects.get(id=6)

        transaction = Transaction(
            portfolio_code=request_body['portfolio_code'],
            security=request_body['security'],
            sec_group=request_body['sec_group'],
            transaction_type=request_body['transaction_type'],
            trade_date=request_body['trade_date'],
            quantity=request_body['quantity'],
            price=request_body['price'],
            currency=request_body['currency'],
            is_active=request_body['is_active'],
            open_status=request_body['open_status'],
            transaction_link_code=request_body['transaction_link_code'],
            option=request_body['option'],
            fx_rate=request_body['fx_rate'],
            broker_id=request_body['broker_id']
        )
        print(request_body['transaction_link_code'], type(request_body['transaction_link_code']))
        if 'id' in request_body:
            transaction.save_transaction(broker_name=account.broker_name, transaction='update', id=request_body['id'])
        elif request_body['transaction_link_code'] != 0:
            transaction.save_transaction(broker_name=account.broker_name, transaction='linked')
        else:
            transaction.save_transaction(broker_name=account.broker_name, transaction='new')
        #     try:
        #         price = Prices.objects.get(date=request_body['trade_date'], inst_code=request_body['security'])
        #         price.price = request_body['price']
        #         price.save()
        #     except Prices.DoesNotExist:
        #         Prices(inst_code=request_body['security'],
        #                date=request_body['trade_date'],
        #                price=request_body['price']).save()
        calculate_holdings(portfolio_code=request_body['portfolio_code'], calc_date=request_body['trade_date'])
        return JsonResponse({"response": "Transaction is created!"}, safe=False)



