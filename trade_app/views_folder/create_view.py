from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from accounts.models import BrokerAccounts
from instrument.models import Instruments, Tickers
from portfolio.models import Portfolio, Transaction, Robots
from trade_app.models import Notifications
from app_functions.request_functions import *
from django.db import connection
import pandas as pd
from broker_apis.oanda import OandaV20
from datetime import date
from app_functions.calculations import calculate_transaction_pnl, calculate_cash_holding


class TradeExecution:
    def __init__(self, parameters):
        self.parameters = parameters
        self.account = BrokerAccounts.objects.get(id=parameters['account_id'])
        self.instrument = Instruments.objects.get(id=parameters['security'])
        self.ticker = Tickers.objects.get(inst_code=parameters['security'],
                                          source=self.account.broker_name)
        self.parameters['currency'] = self.instrument.currency
        self.parameters['sec_group'] = self.instrument.group
        self.parameters['trade_date'] = date.today()
        if self.ticker.margin == 0.0:
            self.parameters['margin'] = 1
        else:
            self.parameters['margin'] = self.ticker.margin
        self.broker_connection = OandaV20(access_token=self.account.access_token,
                                          account_id=self.account.account_number,
                                          environment=self.account.env)

    def new_trade_execution_at_broker(self):
        if self.parameters['transaction_type'] == "Purchase":
            multiplier = 1
        else:
            multiplier = -1
        # Trade execution at broker
        trade = self.broker_connection.submit_market_order(security=self.ticker.source_ticker,
                                                           quantity=float(self.parameters['quantity']) * multiplier)
        if trade['status'] == 'rejected':
            Notifications(portfolio_code=self.parameters['portfolio_code'],
                          message=self.parameters['transaction_type'] + ' ' + self.instrument.name + ' ' + self.parameters[
                              'quantity'],
                          sub_message='Rejected - ' + trade['response']['reason'],
                          broker_name=self.account.broker_name).save()
            return {'response': 'Transaction is rejected. Reason: ' + trade['response']['reason']}

        self.parameters['price'] = trade['response']["price"]
        self.parameters['broker_id'] = trade['response']['id']
        self.parameters['open_status'] = 'Open'
        self.save_transaction(parameters=self.parameters, linked_transaction=False)
        calculate_cash_holding(portfolio_code=self.parameters['portfolio_code'],
                               start_date=self.parameters['trade_date'],
                               currency=self.parameters['currency'])
        Notifications(portfolio_code=self.parameters['portfolio_code'],
                      message=self.parameters['transaction_type'] + ' ' + self.instrument.name + ' ' + self.parameters[
                          'quantity'] + ' @ ' + self.parameters['price'],
                      sub_message='Executed',
                      broker_name=self.account.broker_name).save()

    def close(self, transaction):
        broker_connection = OandaV20(access_token=self.account.access_token,
                                     account_id=self.account.account_number,
                                     environment=self.account.env)
        trade = broker_connection.close_trade(trd_id=transaction['broker_id'])

        self.parameters['price'] = trade["price"]
        self.parameters['broker_id'] = trade['id']
        self.parameters['quantity'] = transaction['quantity']
        self.parameters['open_status'] = 'Close Out'
        self.parameters['transaction_link_code'] = transaction['id']
        if transaction['transaction_type'] == 'Purchase':
            self.parameters['transaction_type'] = 'Sale'
        else:
            self.parameters['transaction_type'] = 'Purchase'
        # self.parameters['id'] = transaction['id']
        dynamic_model_update(table_object=Transaction,
                             request_object={'id': transaction['id'],
                                             'open_status': 'Closed'})
        self.save_transaction(parameters=self.parameters, linked_transaction=True)
        calculate_cash_holding(portfolio_code=self.parameters['portfolio_code'],
                               start_date=self.parameters['trade_date'],
                               currency=self.parameters['currency'])
        Notifications(portfolio_code=self.parameters['portfolio_code'],
                      message='Close ' + self.instrument.name + ' @ ' + self.parameters['price'] + ' Broker ID ' +
                              str(transaction['broker_id']),
                      sub_message='Close',
                      broker_name=self.account.broker_name).save()

    def save_transaction(self, parameters, linked_transaction=False):
        # Main transaction
        # if linked_transaction is True:
        #     transaction_id = parameters['id']
        #     parameters.pop('id')
        #     self.parameters['transaction_link_code'] = transaction_id
        #     dynamic_model_create(table_object=Transaction(),
        #                          request_object=self.parameters)
        # else:
        #     transaction_id = dynamic_model_create(table_object=Transaction(),
        #                                           request_object=self.parameters).id

        transaction_id = dynamic_model_create(table_object=Transaction(),
                                              request_object=self.parameters).id

        # Cashflow transaction
        Transaction(portfolio_code=parameters['portfolio_code'],
                    security='Cash',
                    sec_group='Cash',
                    quantity=float(parameters['quantity']) * float(parameters['price']) * float(parameters['margin']),
                    price=1,
                    currency=parameters['currency'],
                    transaction_type=parameters['transaction_type'] + ' Settlement',
                    transaction_link_code=transaction_id,
                    trade_date=parameters['trade_date'],
                    margin=parameters['margin']).save()

        # Margin trade if the security is CFD
        if self.instrument.group == 'CFD':
            Transaction(portfolio_code=parameters['portfolio_code'],
                        security='Margin',
                        sec_group='Margin',
                        quantity=float(parameters['quantity']) * float(parameters['price']) * (
                                    1 - float(parameters['margin'])),
                        price=1,
                        currency=parameters['currency'],
                        transaction_type=parameters['transaction_type'],
                        transaction_link_code=transaction_id,
                        trade_date=parameters['trade_date'],
                        margin=1 - float(parameters['margin'])).save()


@csrf_exempt
def new_transaction_signal(request):
    if request.method == "POST":
        request_body = json.loads(request.body.decode('utf-8'))
        execution = TradeExecution(parameters=request_body)
        if request_body['transaction_type'] == "Close All":
            open_transactions = Transaction.objects.filter(security=request_body['security'],
                                                           open_status='Open',
                                                           portfolio_code=request_body['portfolio_code']).values()
            for transaction in open_transactions:
                execution.close(transaction=transaction)
        elif request_body['transaction_type'] == 'Close Out':
            execution.close(broker_id=request_body['broker_id'])
        elif request_body['transaction_type'] == 'Close':
            # request_body = {'portfolio_code': 'TST',
            #                 'account_id': 6,
            #                 'security': 74,
            #                 'transaction_type': 'Close',
            #                 'quantity': 1,
            #                 }
            transaction = Transaction.objects.filter(id=request_body['id']).values()[0]
            execution.close(transaction=transaction)
        else:
            # request_body = {'portfolio_code': 'TST',
            #                 'account_id': 6,
            #                 'security': 74,
            #                 'transaction_type': 'Close',
            #                 'quantity': 1,
            #                 }
            execution.new_trade_execution_at_broker()
        return JsonResponse({}, safe=False)
