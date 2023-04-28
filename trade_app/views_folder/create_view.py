from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from accounts.models import BrokerAccounts
from instrument.models import Instruments, Tickers
from portfolio.models import Portfolio, Transaction, Robots
from app_functions.request_functions import *
from django.db import connection
import pandas as pd
from broker_apis.oanda import OandaV20
from datetime import date


def close_transaction(request_body):
    account = BrokerAccounts.objects.get(id=request_body['account_id'])
    ticker = Tickers.objects.get(inst_code=request_body['security'],
                                 source=account.broker_name)
    broker_connection = OandaV20(access_token=account.access_token,
                                 account_id=account.account_number,
                                 environment=account.env)
    trade = broker_connection.close_trade(trd_id=request_body['broker_id'])
    dynamic_model_update(table_object=Transaction,
                             request_object={'id': request_body['id'],
                                             'open_status': 'Closed'})
    request_body['price'] = trade['price']
    request_body['account_id'] = account.id
    request_body['trade_date'] = date.today()
    request_body['broker_id'] = trade['id']
    request_body['margin'] = ticker.margin
    if request_body['transaction_type'] == 'Purchase':
        request_body['transaction_type'] = 'Sale'
    elif request_body['transaction_type'] == 'Sale':
        request_body['transaction_type'] = 'Purchase'
    elif request_body['transaction_type'] == 'Asset In':
        request_body['transaction_type'] = 'Asset Out'
    else:
        request_body['transaction_type'] = 'Asset In'
    request_body['transaction_link_code'] = request_body['id']
    request_body['open_status'] = 'Close Out'
    del request_body['id']
    transaction = dynamic_model_create(table_object=Transaction(),
                                       request_object=request_body)
    return {'response': 'Transaction is closed',
                         'transaction_id': transaction.id}


def new_port_transaction(request_body):
    account = BrokerAccounts.objects.get(id=request_body['account_id'])  #
    instrument = Instruments.objects.get(id=request_body['security'])
    ticker = Tickers.objects.get(inst_code=request_body['security'],
                                 source=account.broker_name)  #
    print(ticker.source_ticker)
    print(instrument.group)
    broker_connection = OandaV20(access_token=account.access_token,
                                 account_id=account.account_number,
                                 environment=account.env)
    if instrument.group == "CFD":
        if request_body['transaction_type'] == "Purchase":
            request_body['transaction_type'] = "Asset In"
        elif request_body['transaction_type'] == "Sale":
            request_body['transaction_type'] = "Asset Out"

    if request_body['transaction_type'] == "Purchase" or request_body['transaction_type'] == "Asset In":
        multiplier = 1
    else:
        multiplier = -1
    trade = broker_connection.submit_market_order(security=ticker.source_ticker,
                                                  quantity=float(request_body['quantity']) * multiplier)
    if trade['status'] == 'rejected':
        return {'response': 'Transaction is rejected. Reason: ' + trade['response']['reason']}

    request_body['price'] = trade['response']["price"]
    request_body['account_id'] = account.id
    request_body['broker_id'] = trade['response']['id']
    request_body['open_status'] = 'Open'
    request_body['currency'] = instrument.currency
    request_body['sec_group'] = instrument.group
    request_body['trade_date'] = date.today()  #
    request_body['margin'] = ticker.margin  #
    transaction = dynamic_model_create(table_object=Transaction(),
                                       request_object=request_body)

    return {'response': 'Transaction is created',
                         'transaction_id': transaction.id}


@csrf_exempt
def new_transaction(request):
    if request.method == "POST":
        request_body = json.loads(request.body.decode('utf-8'))
        response = new_port_transaction(request_body=request_body)
        return JsonResponse(response, safe=False)


@csrf_exempt
def new_transaction_signal(request):
    if request.method == "POST":
        request_body = json.loads(request.body.decode('utf-8'))
        # request_body = {'portfolio_code': 'TST',
        #                 'account_id': 6,
        #                 'security': 74,
        #                 'transaction_type': 'Close',
        #                 'quantity': 1
        #                 }

        if request_body['transaction_type'] == "Close":
            open_transactions = Transaction.objects.filter(security=request_body['security'],
                                                           open_status='Open',
                                                           portfolio_code=request_body['portfolio_code']).values()
            for transaction in open_transactions:
                close_transaction(transaction)
        else:
            new_port_transaction(request_body=request_body)
        return JsonResponse({}, safe=False)
