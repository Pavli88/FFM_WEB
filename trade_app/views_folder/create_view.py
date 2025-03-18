from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from accounts.models import BrokerAccounts
from instrument.models import Instruments, Tickers, Prices
from portfolio.models import Portfolio, Transaction, Nav, TradeRoutes
from trade_app.models import Notifications
import pandas as pd
from broker_apis.oanda import OandaV20
from datetime import date
from calculations.processes.valuation.valuation import calculate_holdings
from django.test import Client
from portfolio.portfolio_functions import create_transaction

class TradeExecution:
    def __init__(self, portfolio_code, account_id, security_id, trade_date):
        self.portfolio = Portfolio.objects.get(portfolio_code=portfolio_code)
        self.account = BrokerAccounts.objects.get(id=account_id)
        self.security_id = security_id
        self.trade_date = trade_date
        self.ticker = Tickers.objects.get(inst_code=self.security_id,
                                          source=self.account.broker_name)

        # It has to be selected based on the account ID which connection has to be established
        self.broker_connection = OandaV20(access_token=self.account.access_token,
                                          account_id=self.account.account_number,
                                          environment=self.account.env)

    def new_trade(self, transaction_type, quantity):
        multiplier = 1 if transaction_type == "Purchase" else -1

        # # Trade execution at broker
        trade = self.broker_connection.submit_market_order(security=self.ticker.source_ticker,
                                                           quantity=float(quantity) * multiplier)
        if trade['status'] == 'rejected':
            Notifications(portfolio_code=self.portfolio.portfolio_code,
                          message=trade['response']['reason'] + ' - ' + transaction_type + ' ' + ' ' + str(quantity),
                          security=self.security_id,
                          sub_message='Rejected',
                          broker_name=self.account.broker_name).save()
            return {'response': 'Transaction is rejected. Reason: ' + trade['response']['reason']}

        trade_price = trade['response']["price"]

        # FX Conversion to Base Currency
        conversion_factor = (float(trade['response']['gainQuoteHomeConversionFactor']) + float(trade['response']['lossQuoteHomeConversionFactor'])) / 2

        transaction = {
            "portfolio_code": self.portfolio.portfolio_code,
            "portfolio_id": self.portfolio.id,
            "security": self.security_id,
            "quantity": quantity,
            "price": trade_price,
            "fx_rate": round(float(conversion_factor), 4),
            "trade_date": self.trade_date.strftime("%Y-%m-%d"),
            "transaction_type": transaction_type,
            "broker": self.account.broker_name,
            "optional": {"account_id": self.account.id, "is_active": True, "broker_id": trade['response']['id']}
        }

        result = create_transaction(transaction)
        print(result)
        # Transaction(
        #     portfolio_code=self.portfolio.portfolio_code,
        #     security_id=self.security_id,
        #     quantity=quantity,
        #     price=trade_price,
        #     fx_rate=round(float(conversion_factor), 4),
        #     trade_date=self.trade_date,
        #     transaction_type=transaction_type,
        #     broker=self.account.broker_name,
        #
        #     broker_id=trade['response']['id'],
        #     account_id=self.account.id,
        #     open_status="Open",
        #     is_active=True
        # ).save()

        Notifications(portfolio_code=self.portfolio.portfolio_code,
                      message=transaction_type + ' ' + ' ' + str(quantity) + ' @ ' + trade_price,
                      sub_message='Executed',
                      security=self.security_id,
                      broker_name=self.account.broker_name).save()

        self.save_price(trade_price=trade_price)

    def get_market_price(self):
        broker_connection = OandaV20(access_token=self.account.access_token,
                                     account_id=self.account.account_number,
                                     environment=self.account.env)
        prices = broker_connection.get_prices(instruments=self.ticker.source_ticker)
        bid = prices['bids'][0]['price']
        ask = prices['asks'][0]['price']
        return (float(bid) + float(ask)) / 2

    def close(self, transaction, quantity=None):
        # BROKER SECTION -----------------------------------------------------------------------------------------------
        broker_connection = OandaV20(access_token=self.account.access_token,
                                     account_id=self.account.account_number,
                                     environment=self.account.env)
        if quantity is not None:
            trade = broker_connection.close_out(trd_id=transaction.broker_id, units=quantity)
        else:
            trade = broker_connection.close_trade(trd_id=transaction.broker_id)
            transaction.is_active = False
            transaction.overwrite()

        # --------------------------------------------------------------------------------------------------------------

        # FX Conversion to Base Currency
        conversion_factor = (float(trade['gainQuoteHomeConversionFactor']) + float(trade['lossQuoteHomeConversionFactor'])) / 2

        # Linked transaction creation
        trade_price = trade["price"]
        broker_id = trade['id']

        transaction = {
            "parent_id": transaction.id,
            "quantity": abs(float(trade['units'])),
            "price": trade_price,
            "fx_rate": round(float(conversion_factor), 4),
            "trade_date": self.trade_date,
            "optional": { "broker_id": broker_id }}

        result = create_transaction(transaction)
        print(result)
        # Transaction(
        #     portfolio_code=self.portfolio.portfolio_code,
        #     security_id=self.security_id,
        #     quantity=abs(float(trade['units'])),
        #     price=trade_price,
        #     fx_rate=round(float(conversion_factor), 4),
        #     trade_date=self.trade_date,
        #     broker_id=broker_id,
        #     broker=self.account.broker_name,
        #     account_id=self.account.id,
        #     transaction_link_code=transaction.id,
        #
        # ).save()

        Notifications(portfolio_code=self.portfolio.portfolio_code,
                      message=' @ ' + trade_price + ' Broker ID ' + str(broker_id),
                      sub_message='Close',
                      security=self.security_id,
                      broker_name=self.account.broker_name).save()

        self.save_price(trade_price=trade_price)

    def save_price(self, trade_price):
        try:
            price = Prices.objects.get(date=self.trade_date, instrument_id=self.security_id)
            price.price = trade_price
            price.save()
        except Prices.DoesNotExist:
            Prices(instrument_id=self.security_id,
                   date=self.trade_date,
                   price=trade_price).save()


@csrf_exempt
def new_transaction_signal(request):
    if request.method == "POST":
        request_body = json.loads(request.body.decode('utf-8'))
        print(request_body)
        trade_date = date.today()

        # OLD Signal
        # request_body = {'portfolio_code': 'TST',
        #                 'account_id': 6,
        #                 'security': 74,
        #                 'transaction_type': 'Close',
        #                 'quantity': 1,
        #                 }
        # NEW Signal
        # request_body = {'portfolio_code': 'TST',
        #                 'security': 74,
        #                 'transaction_type': 'Close',
        #                 'quantity': 1,
        #                 }

        # Close transaction from the Risk view
        if request_body['transaction_type'] == 'risk_closure':
            transactions = pd.DataFrame(Transaction.objects.filter(id__in=request_body['ids']).values())
            for index, transaction in transactions.iterrows():
                execution = TradeExecution(portfolio_code=transaction['portfolio_code'],
                                           account_id=transaction['account_id'],
                                           security=transaction['security'],
                                           trade_date=trade_date)
                closed_transactions = pd.DataFrame(Transaction.objects.filter(transaction_link_code=transaction['id']).values())
                if len(closed_transactions) == 0:
                    closed_out_units = 0
                else:
                    closed_out_units = closed_transactions['quantity'].sum()
                quantity = transaction['quantity'] - abs(closed_out_units)
                execution.close(transaction=transaction, quantity=quantity)
            return JsonResponse('Transactions are closed', safe=False)

        # Checking if trade routing exists
        try:
            routing = TradeRoutes.objects.get(portfolio_code=request_body['portfolio_code'],
                                              inst_id=request_body['security_id'])
        except:
            Notifications(portfolio_code=request_body['portfolio_code'],
                          message='Missing trade routing. Security Code: ' + str(request_body['security_id']),
                          sub_message='Error',
                          broker_name='-').save()
            return JsonResponse({}, safe=False)

        if routing.is_active == 0:
            Notifications(portfolio_code=request_body['portfolio_code'],
                          message='Rejected Trade. Inactive Routing. Security: ' + str(request_body['security_id']),
                          sub_message='Inactive trade routing',
                          broker_name='-').save()
            return JsonResponse({}, safe=False)

        # This code determines if trade routing quantity has to be applied or manual quantity multiplier
        if 'manual' in request_body:
            quantity_multiplier = 1
            account_id = request_body['account_id']
        else:
            quantity_multiplier = routing.quantity
            account_id = routing.broker_account_id

        # Initalizing trade execution
        # Account ID determines the broker and the broker account to trade on
        execution = TradeExecution(portfolio_code=request_body['portfolio_code'],
                                   account_id=account_id,
                                   security_id=request_body['security_id'],
                                   trade_date=trade_date)

        if request_body['transaction_type'] == "Close All":
            open_transactions = Transaction.objects.filter(security=request_body['security_id'],
                                                           is_active=1,
                                                           portfolio_code=request_body['portfolio_code'])
            for transaction in open_transactions:
                execution.close(transaction=transaction)

        # Liquidating the whole portfolio and open trades at the same time
        elif request_body['transaction_type'] == 'Liquidate':
            open_transactions = Transaction.objects.filter(is_active=1,
                                                           portfolio_code=request_body['portfolio_code'])
            for transaction in open_transactions:
                execution.close(transaction=transaction)

        # Partial close out of an existing position
        elif request_body['transaction_type'] == 'Close Out':
            transaction = Transaction.objects.get(id=request_body['id'])
            execution.close(transaction=transaction, quantity=request_body['quantity'])

        # Closing a single open trade with the rest outstanding quantity
        elif request_body['transaction_type'] == 'Close':
            transaction = Transaction.objects.get(id=request_body['id'])
            # print('PARENT')
            # print(transaction)
            execution.close(transaction=transaction)

        # This is the trade execution
        else:
            if 'sl' in request_body:
                latest_nav = list(Nav.objects.filter(portfolio_code=request_body['portfolio_code']).order_by('date').values_list('total', flat=True))[-1]
                risked_amount = latest_nav * float(request_body['risk_perc'])
                current_price = execution.get_market_price()
                price_diff = abs(current_price-float(request_body['sl']))
                quantity = str(int(risked_amount / price_diff))
                request_body['quantity'] = quantity
            execution.new_trade(transaction_type=request_body['transaction_type'],
                                quantity=float(request_body['quantity']) * quantity_multiplier)
        # calculate_holdings(portfolio_code=request_body['portfolio_code'], calc_date=trade_date)
        return JsonResponse({}, safe=False)
