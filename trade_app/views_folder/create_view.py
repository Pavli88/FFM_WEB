from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from accounts.models import BrokerAccounts
from instrument.models import Instruments, Tickers, Prices
from portfolio.models import Portfolio, Transaction, Robots
from trade_app.models import Notifications
from app_functions.request_functions import *
from django.db import connection
import pandas as pd
from broker_apis.oanda import OandaV20
from datetime import date
from app_functions.calculations import calculate_holdings


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
        self.parameters['transaction_link_code'] = ''
        self.save_transaction(request_body=self.parameters)

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
        self.parameters['transaction_link_code'] = transaction['id']
        if transaction['transaction_type'] == 'Purchase':
            self.parameters['transaction_type'] = 'Sale'
        else:
            self.parameters['transaction_type'] = 'Purchase'
        dynamic_model_update(table_object=Transaction,
                             request_object={'id': transaction['id'],
                                             'is_active': 0})
        self.parameters['is_active'] = 0
        self.save_transaction(request_body=self.parameters)

        Notifications(portfolio_code=self.parameters['portfolio_code'],
                      message='Close ' + self.instrument.name + ' @ ' + self.parameters['price'] + ' Broker ID ' +
                              str(transaction['broker_id']),
                      sub_message='Close',
                      broker_name=self.account.broker_name).save()

    def save_transaction(self, request_body):
        # New transaction
        if request_body['transaction_link_code'] == '':
            # With margin
            if request_body['sec_group'] == 'CFD':
                if request_body['transaction_type'] == 'Purchase':
                    request_body['net_cashflow'] = float(request_body['quantity']) * float(
                        request_body['price']) * request_body['margin'] * -1
                    request_body['margin_balance'] = float(request_body['quantity']) * float(
                        request_body['price']) * (1 - request_body['margin'])
            # Without margin
            else:
                if request_body['transaction_type'] == 'Purchase':
                    request_body['net_cashflow'] = float(request_body['quantity']) * float(request_body['price']) * -1
                else:
                    request_body['net_cashflow'] = float(request_body['quantity']) * float(request_body['price'])
            dynamic_model_create(table_object=Transaction(),
                                 request_object=request_body)
        else:
            # Linked transaction
            main_transaction = Transaction.objects.get(id=request_body['transaction_link_code'])
            transaction_weight = abs(float(request_body['quantity']) / float(main_transaction.quantity))

            if main_transaction.transaction_type == 'Purchase':
                pnl = float(request_body['quantity']) * (
                        float(request_body['price']) - float(main_transaction.price))
                net_cf = (transaction_weight * main_transaction.net_cashflow * -1) + pnl
                margin_balance = transaction_weight * main_transaction.margin_balance * -1
            else:
                pnl = float(request_body['quantity']) * (float(main_transaction.price) - float(request_body['price']))
                net_cf = (transaction_weight * main_transaction.net_cashflow * -1) + pnl
                margin_balance = transaction_weight * main_transaction.margin_balance

            print('WEIGHT', transaction_weight)
            print('PNL', pnl)
            print('NET CF', (transaction_weight * main_transaction.net_cashflow) + pnl)
            request_body['realized_pnl'] = pnl
            request_body['net_cashflow'] = net_cf
            request_body['margin_balance'] = margin_balance
            dynamic_model_create(table_object=Transaction(),
                                 request_object=request_body)

        try:
            price = Prices.objects.get(date=request_body['trade_date'], inst_code=request_body['security'])
            price.price = request_body['price']
            price.save()
        except Prices.DoesNotExist:
            Prices(inst_code=request_body['security'],
                   date=request_body['trade_date'],
                   price=request_body['price']).save()
        calculate_holdings(portfolio_code=request_body['portfolio_code'], calc_date=request_body['trade_date'])


@csrf_exempt
def new_transaction_signal(request):
    if request.method == "POST":
        request_body = json.loads(request.body.decode('utf-8'))
        execution = TradeExecution(parameters=request_body)
        if request_body['transaction_type'] == "Close All":
            open_transactions = Transaction.objects.filter(security=request_body['security'],
                                                           is_active=1,
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
