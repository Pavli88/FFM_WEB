from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from accounts.models import BrokerAccounts, BrokerCredentials, Brokers
from instrument.models import Instruments, Tickers, Prices
from portfolio.models import Portfolio, Transaction, Nav, TradeRoutes
from trade_app.models import Notifications
import pandas as pd
from broker_apis.oanda import OandaV20
from broker_apis.capital import CapitalBrokerConnection
from datetime import date
from calculations.processes.valuation.valuation import calculate_holdings
from portfolio.portfolio_functions import create_transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

BROKER_API_CLASSES = {
    'oanda': OandaV20,
    'CPTL': CapitalBrokerConnection,
}

class TradeExecution:
    def __init__(self, portfolio_code, account_id, security_id):
        self.portfolio = Portfolio.objects.get(portfolio_code=portfolio_code)
        self.security_id = security_id
        self.trade_date = timezone.now().strftime('%Y-%m-%d')

        # Account and Broker Credentials
        self.account = BrokerAccounts.objects.get(id=account_id) # -> from here comes the account number
        self.broker = Brokers.objects.get(id=self.account.broker_id)

        try:
            self.broker_credentials = BrokerCredentials.objects.get(broker=self.account.broker, user=self.account.user)
        except BrokerCredentials.DoesNotExist:
            Notifications(portfolio_code=self.portfolio.portfolio_code,
                          message='Rejected Trade. Missing Credentials: ' + str(self.broker.broker_code),
                          sub_message='Missing Credentials',
                          broker_name='-').save()
            raise ValueError("Credentials for this broker are missing.")

        # Instrument Ticker
        try:
            self.ticker = Tickers.objects.get(inst_code=self.security_id,
                                              source=self.broker.broker_code)
        except Tickers.DoesNotExist:
            Notifications(portfolio_code=self.portfolio.portfolio_code,
                          message='Rejected Trade. Missing Ticker: ' + str(self.security_id),
                          sub_message='Missing Ticker: ' + str(self.broker.broker_code) + ' broker. Security Code: ' + str(self.security_id),
                          broker_name='-').save()
            raise ValueError("Ticker for this security is missing at" + str(self.broker.broker_code) + " broker.")

        # Select Broker API Class
        broker_api_class = BROKER_API_CLASSES.get(self.broker.broker_code)

        if broker_api_class is None:
            raise Exception(f"Unsupported broker: {self.broker.broker_code}")

        # Bridge to connect particular API
        self.broker_connection =  broker_api_class.from_credentials(self.broker_credentials, self.account)

    def new_trade(self, transaction_type, quantity):
        multiplier = 1 if transaction_type == "Purchase" else -1

        # Trade execution at broker
        trade = self.broker_connection.submit_market_order(security=self.ticker.source_ticker,
                                                           quantity=float(quantity) * multiplier)
        if trade['status'] == 'rejected':
            Notifications(portfolio_code=self.portfolio.portfolio_code,
                          message=trade['reason'] + ' - ' + transaction_type + ' ' + ' ' + str(quantity),
                          security=self.security_id,
                          sub_message='Rejected',
                          broker_name=self.account.broker_name).save()
            return {'response': 'Transaction is rejected. Reason: ' + trade['reason']}

        # Creating transaction at platform
        transaction = {
            "portfolio_code": self.portfolio.portfolio_code,
            "portfolio_id": self.portfolio.id,
            "security": self.security_id,
            "quantity": quantity,
            "price": trade['trade_price'],
            "fx_rate": round(float(trade['fx_rate']), 4),
            "trade_date": self.trade_date,
            "transaction_type": transaction_type,
            "broker": self.broker.broker_code, # self.account.broker_name
            "optional": {"account_id": self.account.id, "is_active": True, "broker_id": trade['broker_id']}
        }

        create_transaction(transaction) # -> Here to add a feature to capture if accounting data was processed sucessfully

        Notifications(portfolio_code=self.portfolio.portfolio_code,
                      message=transaction_type + ' ' + ' ' + str(quantity) + ' @ ' + str(trade['trade_price']),
                      sub_message='Executed',
                      security=self.security_id,
                      broker_name=self.account.broker_name).save()

        self.save_price(trade_price=trade['trade_price'])

    def get_market_price(self):
        prices = self.broker_connection.get_prices(instruments=self.ticker.source_ticker)
        bid = prices['bids'][0]['price']
        ask = prices['asks'][0]['price']
        return (float(bid) + float(ask)) / 2

    def close(self, transaction, quantity=None):

        # Close Out
        if quantity is not None:
            trade = self.broker_connection.close_out(trd_id=transaction.broker_id, units=quantity)
        # Full Close
        else:
            trade = self.broker_connection.close_trade(trd_id=transaction.broker_id)
            transaction.is_active = False
            transaction.overwrite()

        # Creating transaction at platform
        transaction = {
            "parent_id": transaction.id,
            "quantity": abs(float(trade['units'])),
            "price": trade["price"],
            "fx_rate": round(float(trade["fx_rate"]), 4),
            "trade_date": self.trade_date,
            "optional": { "broker_id": trade['broker_id'] }}

        create_transaction(transaction)

        Notifications(portfolio_code=self.portfolio.portfolio_code,
                      message=' @ ' + str(trade["price"]) + ' Broker ID ' + str(trade['broker_id']),
                      sub_message='Close',
                      security=self.security_id,
                      broker_name=self.account.broker_name).save()

        self.save_price(trade_price=trade["price"])


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
                                           )
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
        try:
            execution = TradeExecution(
                portfolio_code=request_body['portfolio_code'],
                account_id=request_body['account_id'],
                security_id=request_body['security_id']
            )
        except ValueError as e:
            return JsonResponse({'response': str(e)})


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


# I will have to review the logic of the trade execution class and rework its functions

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def close_trade_by_id(request):
    try:
        # Parse JSON request body
        request_body = json.loads(request.body.decode('utf-8'))
        transaction_ids = request_body.get("ids", [])

        # Check if transaction_ids is a valid list
        if not isinstance(transaction_ids, list) or not transaction_ids:
            return JsonResponse({"error": "Invalid or missing transaction IDs"}, status=400)

        open_transactions = Transaction.objects.filter(id__in=transaction_ids)
        for transaction in open_transactions:
            execution = TradeExecution(portfolio_code=transaction.portfolio_code,
                                       account_id=transaction.account_id,
                                       security_id=transaction.security_id,
                                       )

            execution.close(transaction=transaction)

        # Return response
        return JsonResponse({
            "message": f"transactions closed successfully",
            "closed_transaction_ids": transaction_ids
        }, status=200)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON data"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def new_trade(request):
    if request.method == "POST":
        request_body = json.loads(request.body.decode('utf-8'))
        print(request_body)

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
                                           )
                closed_transactions = pd.DataFrame(
                    Transaction.objects.filter(transaction_link_code=transaction['id']).values())
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
        try:
            execution = TradeExecution(
                portfolio_code=request_body['portfolio_code'],
                account_id=request_body['account_id'],
                security_id=request_body['security_id']
            )
        except ValueError as e:
            return JsonResponse({'response': str(e)})

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
                latest_nav = list(
                    Nav.objects.filter(portfolio_code=request_body['portfolio_code']).order_by('date').values_list(
                        'total', flat=True))[-1]
                risked_amount = latest_nav * float(request_body['risk_perc'])
                current_price = execution.get_market_price()
                price_diff = abs(current_price - float(request_body['sl']))
                quantity = str(int(risked_amount / price_diff))
                request_body['quantity'] = quantity
            execution.new_trade(transaction_type=request_body['transaction_type'],
                                quantity=float(request_body['quantity']) * quantity_multiplier)
        # calculate_holdings(portfolio_code=request_body['portfolio_code'], calc_date=trade_date)
        return JsonResponse({}, safe=False)
