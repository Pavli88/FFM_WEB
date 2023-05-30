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
    def __init__(self, portfolio_code, account_id, security, trade_date):
        self.portfolio = Portfolio.objects.get(portfolio_code=portfolio_code)
        self.account = BrokerAccounts.objects.get(id=account_id)
        self.security = Instruments.objects.get(id=security)
        self.trade_date = trade_date

        self.broker_connection = OandaV20(access_token=self.account.access_token,
                                          account_id=self.account.account_number,
                                          environment=self.account.env)

    def new_trade(self, transaction_type, quantity):
        ticker = Tickers.objects.get(inst_code=self.security.id,
                                     source=self.account.broker_name)
        if ticker.margin == 0.0:
            margin = 1
        else:
            margin = ticker.margin

        if transaction_type == "Purchase":
            multiplier = 1
        else:
            multiplier = -1

        # # Trade execution at broker
        trade = self.broker_connection.submit_market_order(security=ticker.source_ticker,
                                                           quantity=float(quantity) * multiplier)
        if trade['status'] == 'rejected':
            Notifications(portfolio_code=self.portfolio.portfolio_code,
                          message=transaction_type + ' ' + self.security.name + ' ' + quantity,
                          sub_message='Rejected - ' + trade['response']['reason'],
                          broker_name=self.account.broker_name).save()
            return {'response': 'Transaction is rejected. Reason: ' + trade['response']['reason']}

        trade_price = trade['response']["price"]

        if self.security.group == 'CFD':
            net_cash_flow = float(quantity) * float(
                trade_price) * margin * -1
            margin_balance = float(quantity) * float(
                trade_price) * (1 - margin)
        # Without margin
        else:
            if transaction_type == 'Purchase':
                net_cash_flow = float(quantity) * float(trade_price) * -1
            else:
                net_cash_flow = float(quantity) * float(trade_price)
            margin_balance = 0.0

        Transaction(
            portfolio_code=self.portfolio.portfolio_code,
            quantity=quantity,
            price=trade_price,
            currency=self.security.currency,
            transaction_type=transaction_type,
            trade_date=self.trade_date,
            security=self.security.id,
            sec_group=self.security.group,
            broker_id=trade['response']['id'],
            account_id=self.account.id,
            margin=margin,
            margin_balance=round(margin_balance, 5),
            net_cashflow=round(net_cash_flow, 5),
        ).save()

        Notifications(portfolio_code=self.portfolio.portfolio_code,
                      message=transaction_type + ' ' + self.security.name + ' ' + quantity + ' @ ' + trade_price,
                      sub_message='Executed',
                      broker_name=self.account.broker_name).save()
        self.save_price(trade_price=trade_price)

    def close(self, transaction, quantity):
        print(transaction)
        broker_connection = OandaV20(access_token=self.account.access_token,
                                     account_id=self.account.account_number,
                                     environment=self.account.env)
        trade = broker_connection.close_trade(trd_id=transaction['broker_id'])

        # Main transaction update
        dynamic_model_update(table_object=Transaction,
                             request_object={'id': transaction['id'],
                                             'is_active': 0})

        # Linked transaction creation
        trade_price = trade["price"]
        broker_id = trade['id']
        transaction_weight = abs(float(quantity) / float(transaction['quantity']))
        if transaction['transaction_type'] == 'Purchase' or transaction['sec_group'] == 'CFD':
            if transaction['transaction_type'] == 'Purchase':
                pnl = float(quantity) * (
                        float(trade_price) - float(transaction['price']))
            else:
                pnl = float(quantity) * (
                         float(transaction['price']) - float(trade_price))
            net_cash_flow = (transaction_weight * float(transaction['net_cashflow']) * -1) + pnl
            margin_balance = transaction_weight * transaction['margin_balance'] * -1
            transaction_type = 'Sale'
        else:
            pnl = float(quantity) * (float(transaction['price']) - float(trade_price))
            net_cash_flow = (transaction_weight * transaction['net_cashflow'] * -1) + pnl
            margin_balance = transaction_weight * transaction['margin_balance']
            transaction_type = 'Purchase'
        Transaction(
            portfolio_code=self.portfolio.portfolio_code,
            quantity=quantity,
            price=trade_price,
            currency=self.security.currency,
            transaction_type=transaction_type,
            trade_date=self.trade_date,
            security=self.security.id,
            sec_group=self.security.group,
            broker_id=broker_id,
            account_id=self.account.id,
            is_active=0,
            realized_pnl=round(pnl, 5),
            margin_balance=round(margin_balance, 5),
            net_cashflow=round(net_cash_flow, 5),
            transaction_link_code=transaction['id']
        ).save()

        Notifications(portfolio_code=self.portfolio.portfolio_code,
                      message='Close ' + self.security.name + ' @ ' + trade_price + ' Broker ID ' +
                              str(broker_id),
                      sub_message='Close',
                      broker_name=self.account.broker_name).save()

        self.save_price(trade_price=trade_price)

    def save_price(self, trade_price):
        try:
            price = Prices.objects.get(date=self.trade_date, inst_code=self.security.id)
            price.price = trade_price
            price.save()
        except Prices.DoesNotExist:
            Prices(inst_code=self.security.id,
                   date=self.trade_date,
                   price=trade_price).save()


@csrf_exempt
def new_transaction_signal(request):
    if request.method == "POST":
        request_body = json.loads(request.body.decode('utf-8'))
        trade_date = date.today()
        # request_body = {'portfolio_code': 'TST',
        #                 'account_id': 6,
        #                 'security': 74,
        #                 'transaction_type': 'Close',
        #                 'quantity': 1,
        #                 }
        print(request_body)
        execution = TradeExecution(portfolio_code=request_body['portfolio_code'],
                                   account_id=request_body['account_id'],
                                   security=request_body['security'],
                                   trade_date=trade_date)

        if request_body['transaction_type'] == "Close All":
            open_transactions = Transaction.objects.filter(security=request_body['security'],
                                                           is_active=1,
                                                           portfolio_code=request_body['portfolio_code']).values()

            for transaction in open_transactions:
                execution.close(transaction=transaction, quantity=transaction['quantity'])

        elif request_body['transaction_type'] == 'Close Out':
            execution.close(broker_id=request_body['broker_id'])
        elif request_body['transaction_type'] == 'Close':
            transaction = Transaction.objects.filter(id=request_body['id']).values()[0]
            execution.close(transaction=transaction, quantity=transaction['quantity'])
        else:
            execution.new_trade(transaction_type=request_body['transaction_type'],
                                quantity=request_body['quantity'])
        calculate_holdings(portfolio_code=request_body['portfolio_code'], calc_date=trade_date)
        return JsonResponse({}, safe=False)
