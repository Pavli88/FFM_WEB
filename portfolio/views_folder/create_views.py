from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from portfolio.models import Robots, Portfolio, CashFlow, Transaction
from instrument.models import Instruments, Tickers
from accounts.models import BrokerAccounts
import json
from app_functions.request_functions import *
from app_functions.calculations import *


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
                             status="active",
                             inception_date=body_data["inception_date"],
                             owner=body_data["owner"])
            port.save()
            return JsonResponse({'msg': "New Portfolio is created!", 'port': port.id}, safe=False)
        except:
            return JsonResponse({'msg': "Portfolio exists in database!", 'port': 0}, safe=False)


@csrf_exempt
def create_cashflow(request):
    if request.method == "POST":
        body_data = json.loads(request.body.decode('utf-8'))
        try:
            CashFlow(
                portfolio_code=body_data['portfolio_code'],
                amount=body_data['amount'],
                type=body_data['type'],
                date=body_data['date'],
                user=body_data['user'],
                currency=body_data['currency']
            ).save()
        except:
            print('Error in cash insert')
        return JsonResponse({"msg": "Cashflow entered into database!"}, safe=False)


@csrf_exempt
def create_transaction(request):
    if request.method == "POST":
        request_body = json.loads(request.body.decode('utf-8'))
        print(request_body)
        if request_body['security'] == 'Cash':
            dynamic_model_create(table_object=Transaction(),
                                 request_object=request_body)
        else:
            account = BrokerAccounts.objects.get(id=6)
            instrument = Instruments.objects.get(id=request_body['security'])
            ticker = Tickers.objects.get(inst_code=request_body['security'],
                                         source=account.broker_name)
            request_body['currency'] = instrument.currency
            request_body['sec_group'] = instrument.group
            request_body['margin'] = ticker.margin
            transaction = dynamic_model_create(table_object=Transaction(),
                                 request_object=request_body)

            if request_body['transaction_link_code'] == '':
                link_id = transaction.id
            else:
                link_id = request_body['transaction_link_code']

            # Cashflow transaction
            Transaction(portfolio_code=request_body['portfolio_code'],
                        security='Cash',
                        sec_group='Cash',
                        quantity=float(request_body['quantity']) * float(request_body['price']) * float(
                            request_body['margin']),
                        price=1,
                        currency=request_body['currency'],
                        transaction_type=request_body['transaction_type'] + ' Settlement',
                        transaction_link_code=link_id,
                        trade_date=request_body['trade_date']).save()

            # Margin trade if the security is CFD
            if instrument.group == 'CFD':
                Transaction(portfolio_code=request_body['portfolio_code'],
                            security='Margin',
                            sec_group='Margin',
                            quantity=float(request_body['quantity']) * float(request_body['price']) * (
                                    1 - float(request_body['margin'])),
                            price=1,
                            currency=request_body['currency'],
                            transaction_type=request_body['transaction_type'],
                            transaction_link_code=link_id,
                            trade_date=request_body['trade_date'],
                            margin=1 - float(request_body['margin'])).save()

        calculate_cash_holding(portfolio_code=request_body['portfolio_code'],
                               start_date=request_body['trade_date'],
                               currency=request_body['currency'])

        return JsonResponse({"response": "Transaction is created!"}, safe=False)


