from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from portfolio.models import Portfolio, Transaction
from instrument.models import Instruments, Tickers
from accounts.models import BrokerAccounts
from app_functions.request_functions import *
from django.db import connection
from broker_apis.oanda import OandaV20
from datetime import date


@csrf_exempt
def close_transaction(request):
    if request.method == "POST":
        request_body = json.loads(request.body.decode('utf-8'))
        print(request_body)
        account = BrokerAccounts.objects.get(id=request_body['account_id'])
        instrument = Instruments.objects.get(id=request_body['security'])
        ticker = Tickers.objects.get(inst_code=request_body['security'],
                                     source=account.broker_name)
        broker_connection = OandaV20(access_token=account.access_token,
                                     account_id=account.account_number,
                                     environment=account.env)
        if request_body['status'] == 'close_all':
            trade = broker_connection.close_trade(trd_id=request_body['broker_id'])
            dynamic_model_update(table_object=Transaction,
                                 request_object={'id': request_body['id'],
                                                 'open_status': 'Closed'})
        else:
            trade = broker_connection.close_out(trd_id=request_body['broker_id'], units=request_body['quantity'])

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
        return JsonResponse({'response': 'Transaction is closed',
                             'transaction_id': transaction.id}, safe=False)
