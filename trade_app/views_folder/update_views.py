from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from portfolio.models import Portfolio, Transaction
from app_functions.request_functions import *
from django.db import connection
from broker_apis.oanda import OandaV20


@csrf_exempt
def close_transaction(request):
    if request.method == "POST":
        request_body = json.loads(request.body.decode('utf-8'))
        transaction = dynamic_model_update(table_object=Transaction,
                                           request_object={'id': request_body['id'],
                                                           'open_status': 'Closed'})

        print(request_body)
        # This part created the opposite cash transaction for the remaining balance
        # The price will come from the broker side
        cursor = connection.cursor()
        cursor.execute(
            """select pr.portfolio_code, it.source_ticker, it.source, ba.account_number, ba.account_name, ba.access_token, ba.env 
            from portfolio_robots as pr, instrument_tickers as it, accounts_brokeraccounts as ba
where pr.ticker_id = it.id and ba.id = pr.broker_account_id
and pr.portfolio_code='{portfolio_code}'
and it.inst_code={instrument_code};""".format(portfolio_code=request_body['portfolio_code'],
                                              instrument_code=request_body['security']))
        row = cursor.fetchall()
        print(row)
        broker_connection = OandaV20(access_token=row[0][5],
                                     account_id=row[0][3],
                                     environment=row[0][6])
        trade = broker_connection.close_trade(trd_id=request_body['broker_id'])
        print(trade)
        request_body['price'] = trade['price']
        request_body['broker'] = row[0][2]
        # request_body['trade_date'] = trade['time']
        request_body['broker_id'] = trade['id']
        del request_body['id']
        print(request_body)
        dynamic_model_create(table_object=Transaction(),
                             request_object=request_body)

        return JsonResponse({'response': 'Transaction is closed',
                             'transaction_id': transaction.id}, safe=False)