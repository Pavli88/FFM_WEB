import oandapy
import pandas as pd
from oandapyV20 import API
import oandapyV20.endpoints.trades as trades
import oandapyV20.endpoints.pricing as pricing
import oandapyV20.endpoints.orders as orders
import json

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', -1)


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

        """
        Function to get all open trades for an account
        :return:
        """

        self.open_trades = self.oanda.trades.get_open_trades(account_id=self.account_number).as_dict()
        self.open_trades_table = pd.DataFrame.from_dict(self.open_trades["trades"])

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

    def account_summary(self):

        self.account_summary = self.oanda.account.get_account_summary(account_id=self.account_number).as_dict()
        self.account_summary_table = pd.DataFrame.from_dict(self.account_summary)
        print(self.account_summary_table)


    def get_transactions(self, start_date, end_date):

        """
        Function to get back all the transactions between the start and ending period.
        :param start_date:
        :param end_date:
        :return:
        """

        self.transactions = self.oanda.transactions.get_transactions(account_id=self.account_number,
                                                                     from_date=start_date,
                                                                     to_date=end_date,
                                                                     page_size=1000).as_dict()

        print("Pages:")
        print(self.transactions["pages"])

        self.transactions_df = pd.DataFrame()

        for page in self.transactions["pages"]:
            self.tr_request = self.oanda.make_request(method_name="GET",
                                                      endpoint=page.partition("v3/")[2])
            self.tr_df = pd.DataFrame.from_dict(self.tr_request.json()["transactions"])
            self.transactions_df = self.transactions_df.append(self.tr_df)

        return self.transactions_df

    def get_transaction_sinceid(self):

        self.transactions = self.oanda.transactions.get_transaction_sinceid(account_id=self.account_number,
                                                                            last_transaction_id=991).as_dict()

        self.transactions_table = pd.DataFrame.from_dict(self.transactions)
        print(self.transactions_table)


    def get_all_trades(self):

        self.trades = self.oanda.trades.get_trades(account_id=self.account_number,
                                                   instrument="EUR_USD").as_dict()
        print(self.trades)

    def trade_details(self, trade_id):

        """
        Function to get trade details for a specific transaction by trade ID
        :param trade_id:
        :return:
        """

        self.trd_details = self.oanda.trades.get_trade_details(account_id=self.account_number,
                                                               trade_id=trade_id).as_dict()

        return self.trd_details

    def get_risk_list(self):

        self.op_trd_table = self.get_open_trades()

        self.df_lenght = range(len(self.op_trd_table["id"]))
        self.price_list = list(self.op_trd_table["price"])
        self.quantity = list(self.op_trd_table["initialUnits"])

        self.risk_list = []

        for i, price, qt in zip(self.df_lenght, self.price_list, self.quantity):

            sl_price = self.open_trades["trades"][i]["stopLossOrder"]["price"]

            if float(qt) < 0:
                self.trd_risk = (float(sl_price) - float(price)) * float(qt)
            else:
                self.trd_risk = (float(price) - float(sl_price)) * float(qt)

            self.risk_list.append(self.trd_risk)

            print("Stopp Loss Price:", sl_price, "Trade Price:", price, "Quantity:", qt, "Risk:", self.trd_risk)

    def pricing_stream(self):
        self.oanda.make_request(method_name="GET", endpoint="accounts/001-004-2840244-004/pricing/stream?instruments=XAG_USD", stream=True)
        print("PRICING STREAM")


class OandaV20:

    """
    Oanda V20 API
    """

    def __init__(self, access_token, account_id):

        """
        OandaV20 API connection with the access token and the account number
        :param access_token:
        :param account_id:
        """

        self.api = API(access_token=access_token)
        self.account_id = account_id

    def pricing_stream(self, instrument):

        """
        Pricing stream on a given instrument
        :param instrument:
        :return:
        """

        params ={"instruments": instrument}

        r = pricing.PricingStream(accountID=self.account_id, params=params)
        rv = self.api.request(r)
        maxrecs = 12

        for ticks in rv:
            print(ticks)
            # print(json.dumps(ticks, indent=4), ",")
            if maxrecs == 0:
                r.terminate("maxrecs records received")

    def submit_market_order(self, security, sl_price, quantity):

        print("============")
        print("MARKET ORDER")
        print("============")

        data = {
            "order": {
                "stopLossOnFill": {
                    "price": sl_price
                },
                "instrument": security,
                "units": quantity,
                "type": "MARKET",
                "positionFill": "DEFAULT"
            }
        }
        print("ORDER:", data)

        r = orders.OrderCreate(self.account_id, data=data)
        self.api.request(r)

        print("Market Order was executed succesfully!")
        print("")

    def get_open_trades(self):

        print("===========")
        print("OPEN TRADES")
        print("===========")

        r = trades.OpenTrades(accountID=self.account_id)
        self.api.request(r)

        open_trades_df = pd.DataFrame.from_dict(r.response["trades"])

        print(open_trades_df)

        return open_trades_df


if __name__ == "__main__":
    #.pricing_stream(instrument="XAG_USD")
    #.submit_market_order(security="XAG_USD", sl_price="24.15", quantity="-10")
    OandaV20(access_token="ecd553338b9feac1bb350924e61329b7-0d7431f8a1a13bddd6d5880b7e2a3eea",
             account_id="101-004-11289420-001").get_open_trades()




