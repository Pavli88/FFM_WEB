from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from accounts.models import BrokerAccounts
from instrument.models import Instruments
from portfolio.models import Portfolio, Transaction, Robots
from instrument.models import Tickers
from app_functions.request_functions import *
from django.db import connection
import pandas as pd
from broker_apis.oanda import OandaV20
from datetime import date


@csrf_exempt
def new_transaction(request):
    if request.method == "POST":
        print('NEW PORTFOLIO LIVE TRANSACTION')
        request_body = json.loads(request.body.decode('utf-8'))
        print(request_body)

        # {'portfolio_code': 'TST',
        #  'account_id': 6,
        #  'security_id': 74,
        #  'transaction_type': 'Purchase',
        #  'quantity': 1}

        account = BrokerAccounts.objects.get(id=request_body['account_id'])
        instrument = Instruments.objects.get(id=request_body['security'])
        broker_connection = OandaV20(access_token=account.access_token,
                                     account_id=account.account_number,
                                     environment=account.env)
        if request_body['transaction_type'] == "Purchase" or request_body['transaction_type'] == "Asset In":
            multiplier = 1
        else:
            multiplier = -1
        trade = broker_connection.submit_market_order(security=request_body['ticker'],
                                                      quantity=float(request_body['quantity'])*multiplier)
        if trade['status'] == 'rejected':
            return JsonResponse({'response': 'Transaction is rejected. Reason: ' + trade['response']['reason']}, safe=False)
        request_body['price'] = trade['response']["price"]
        request_body['account_id'] = account.id
        request_body['broker_id'] = trade['response']['id']
        request_body['open_status'] = 'Open'
        request_body['currency'] = instrument.currency
        request_body['sec_group'] = instrument.group
        request_body['trade_date'] = date.today()
        transaction = dynamic_model_create(table_object=Transaction(),
                                           request_object=request_body)

        return JsonResponse({'response': 'Transaction is created',
                             'transaction_id': transaction.id}, safe=False)
