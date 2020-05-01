import oandapy
import pandas as pd

class Oanda:

    def __init__(self, environment, acces_token, account_number):
        self.account_number = account_number
        self.oanda = oandapy.APIv20(environment=environment, access_token=acces_token)
        print("Oanda instance creation is successful")

    def submit_order(self, order):
        print("Submitting order...")
        self.oanda.orders.create_order(account_id=self.account_number, order=order)

    def bid_ask(self, security):

        """
        Function returns the best bids and asks for a security.
        :param security:
        :return:
        """

        self.bid_ask = self.oanda.pricing.get_pricing(account_id=self.account_number,
                                                      instruments=[security]).as_dict()

        self.bids = pd.DataFrame.from_dict(self.bid_ask["prices"][0]["bids"])
        self.asks = pd.DataFrame.from_dict(self.bid_ask["prices"][0]["asks"])
        self.ask = list(self.asks["price"])[0]
        self.bid = list(self.bids["price"])[-1]

        return {"ask": self.ask, "bid": self.bid}

    def get_account_data(self):

        """
        Gets basic account information.
        :return:
        """

        self.account_data = self.oanda.account.get_account(account_id=self.account_number).as_dict()

        return self.account_data

    def get_open_trades(self):

        self.open_trades = self.oanda.trades.get_open_trades(account_id=self.account_number).as_dict()
        self.open_trades_table = pd.DataFrame.from_dict(self.open_trades["trades"])

        print(self.open_trades_table)

        return self.open_trades_table

    def close_all_positions(self, open_trades_table):

        """
        Closes all trades for a security
        :param open_trades_table:
        :return:
        """

        print("Closing all positions")
        print("Position:")

        for id in list(open_trades_table["id"]):
            self.oanda.trades.close_trade(account_id=self.account_number, trade_id=id, units="ALL")
            print("Trade:", id)

