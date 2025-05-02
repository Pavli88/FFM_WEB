from accounts.models import BrokerAccounts, BrokerCredentials, Brokers
from instrument.models import Tickers, Prices
from portfolio.models import Portfolio
from trade_app.models import Notifications
from broker_apis.oanda import OandaV20
from broker_apis.capital import CapitalBrokerConnection
from portfolio.portfolio_functions import create_transaction
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