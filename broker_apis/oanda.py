import pandas as pd
from oandapyV20 import API
import oandapyV20.endpoints.trades as trades
import oandapyV20.endpoints.pricing as pricing
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.instruments as instruments
import oandapyV20.endpoints.positions as positions


class OandaV20:
    def __init__(self, access_token, account_id, environment):

        if environment == 'demo':
            self.env = 'practice'
        else:
            self.env = 'live'
        self.api = API(access_token=access_token, environment=self.env)
        self.account_id = account_id

    def pricing_stream(self, instrument):
        params ={"instruments": instrument}
        r = pricing.PricingStream(accountID=self.account_id, params=params)
        rv = self.api.request(r)
        return rv

    def submit_market_order(self, security, quantity, sl_price=None):
        if sl_price is None:
            data = {
                "order": {
                    "instrument": security,
                    "units": quantity,
                    "type": "MARKET",
                    "positionFill": "DEFAULT"
                }
            }
        else:
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
        response = r.response

        if list(response.keys())[1] == 'orderFillTransaction':
            print("ACCEPTED TRADE")
            response = response['orderFillTransaction']
            status = 'accepted'
        if list(response.keys())[1] == 'orderCancelTransaction':
            print("REJECTED TRADE")
            print("REASON:", response['orderCancelTransaction']['reason'])
            response = response['orderCancelTransaction']
            status = 'rejected'
        return {'response': response, 'status': status}

    def get_open_trades(self):

        print("===========")
        print("OPEN TRADES")
        print("===========")

        r = trades.OpenTrades(accountID=self.account_id)
        self.api.request(r)

        open_trades_df = pd.DataFrame.from_dict(r.response["trades"])

        print(open_trades_df)

        return open_trades_df

    def close_trade(self, trd_id):
        r = trades.TradeClose(accountID=self.account_id, tradeID=trd_id)
        self.api.request(r)
        response = r.response
        return response['orderFillTransaction']

    def close_out(self , trd_id, units):
        r = trades.TradeClose(accountID=self.account_id, tradeID=trd_id, data={"units": units})
        self.api.request(r)
        response = r.response
        return response['orderFillTransaction']

    def get_prices(self, instruments):

        params = {
            "instruments": instruments
        }

        r = pricing.PricingInfo(accountID=self.account_id, params=params)
        self.api.request(r)

        response = r.response

        return response['prices'][0]

    def get_prices_2(self, instruments):

        params = {
            "instruments": instruments
        }

        r = pricing.PricingInfo(accountID=self.account_id, params=params)
        self.api.request(r)

        response = r.response

        return response['prices']

    def candle_data(self, instrument, params):
        r = instruments.InstrumentsCandles(instrument=instrument, params = params)
        self.api.request(r)
        return r.response

    def position_list(self):
        r = positions.PositionList(accountID=self.account_id)
        self.api.request(r)
        return r.response

if __name__ == "__main__":
    o = OandaV20(access_token="acc56198776d1ce7917137567b23f9a1-c5f7a43c7c6ef8563d0ebdd4a3b496ac",
                 account_id="001-004-2840244-004",
                 environment="live")

    params = {
        "granularity": 'D',
        "from": "2023-01-01",
        "to": "2023-10-04"
    }

    data = o.candle_data(instrument='HUF_USD',
                         params=params)
    print(data)
