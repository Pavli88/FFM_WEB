from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from portfolio.models import Portfolio, Transaction, Robots
from instrument.models import Tickers
from app_functions.request_functions import *
from django.db import connection
import pandas as pd
from broker_apis.oanda import OandaV20


@csrf_exempt
def new_transaction(request):
    if request.method == "POST":
        print('NEW PORTFOLIO LIVE TRANSACTION')
        request_body = json.loads(request.body.decode('utf-8'))
        print(request_body)

        # Instrument mapping query on portfolio
        cursor = connection.cursor()
        cursor.execute(
            """select pr.portfolio_code, it.source_ticker, it.source, ba.account_number, ba.account_name, ba.access_token, ba.env from portfolio_robots as pr, instrument_tickers as it, accounts_brokeraccounts as ba
where pr.ticker_id = it.id and ba.id = pr.broker_account_id
and pr.portfolio_code='{portfolio_code}'
and it.inst_code={instrument_code};""".format(portfolio_code=request_body['portfolio_code'],
                                               instrument_code=request_body['security'])
        )
        row = cursor.fetchall()
        print(row[0])
        print(row[0][3])

        broker_connection = OandaV20(access_token=row[0][5],
                                     account_id=row[0][3],
                                     environment=row[0][6])

        trade = broker_connection.submit_market_order(security=row[0][1],
                                                      quantity=request_body['quantity'])
        print(trade)

        request_body['price'] = trade['response']["price"]
        request_body['broker'] = row[0][2]
        request_body['broker_id'] = trade['response']['id']
        # Selecting broker routing and execute trade at broker

        # This part saves the transaction to db
        transaction = dynamic_model_create(table_object=Transaction(),
                                           request_object=request_body)

        return JsonResponse({'response': 'Transaction is created',
                             'transaction_id': transaction.id}, safe=False)
