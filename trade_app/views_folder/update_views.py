from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from portfolio.models import Portfolio, Transaction
from accounts.models import BrokerAccounts
from app_functions.request_functions import *
from django.db import connection
from broker_apis.oanda import OandaV20
from datetime import date


@csrf_exempt
def close_transaction(request):
    if request.method == "POST":
        request_body = json.loads(request.body.decode('utf-8'))

        account = BrokerAccounts.objects.get(id=request_body['account_id'])
        broker_connection = OandaV20(access_token=account.access_token,
                                     account_id=account.account_number,
                                     environment=account.env)

        trade = broker_connection.close_trade(trd_id=request_body['broker_id'])
        print(request_body)
        print(trade)
        request_body['price'] = trade['price']
        request_body['account_id'] = account.id
        request_body['trade_date'] = date.today()
        request_body['broker_id'] = trade['id']

        if request_body['transaction_type'] == 'Purchase':
            request_body['transaction_type'] = 'Sale'
        else:
            request_body['transaction_type'] = 'Purchase'

        request_body['transaction_link_code'] = request_body['id']
        request_body['open_status'] = 'Close Out'

        print(request_body)

        transaction = dynamic_model_update(table_object=Transaction,
                                           request_object={'id': request_body['id'],
                                                           'open_status': 'Closed'})
        del request_body['id']
        dynamic_model_create(table_object=Transaction(),
                             request_object=request_body)

        return JsonResponse({'response': 'Transaction is closed',
                             'transaction_id': transaction.id}, safe=False)