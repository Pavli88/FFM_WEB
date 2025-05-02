from broker_apis.oanda import OandaV20
from instrument.models import Tickers, Prices
from datetime import datetime, timedelta
from accounts.models import BrokerAccounts

def oanda_pricing(start_date, end_date):
    tickers = Tickers.objects.filter(source='oanda').values()
    print(tickers)
    accounts = BrokerAccounts.objects.get(id=2)

    o = OandaV20(access_token=accounts.access_token,
                 account_id=accounts.account_number,
                 environment="live")
    params = {
        "granularity": 'D',
        "from": start_date,
        "to": end_date
    }

    for ticker in tickers:
        print(ticker['source_ticker'], ticker['inst_code_id'])
        response = o.candle_data(instrument=ticker['source_ticker'],
                                 params=params)['candles']

        for data in response:
            date = datetime.strptime(data['time'][0:10], "%Y-%m-%d") + timedelta(days=1)
            print(date, data['mid']['c'])

            try:
                price = Prices.objects.get(date=date,
                                           instrument_id=int(ticker['inst_code_id']))
                price.price = float(data['mid']['c'])
                price.save()
            except:
                Prices(date=date,
                       instrument_id=int(ticker['inst_code_id']),
                       price=float(data['mid']['c']),
                       source='oanda'
                       ).save()
    return ''