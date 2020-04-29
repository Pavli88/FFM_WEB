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

