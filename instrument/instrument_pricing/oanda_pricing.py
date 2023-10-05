from broker_apis.oanda import OandaV20
from instrument.models import Tickers, Prices
from datetime import datetime, timedelta


def oanda_pricing(start_date, end_date):
    tickers = Tickers.objects.filter(source='oanda').values()
    o = OandaV20(access_token="acc56198776d1ce7917137567b23f9a1-c5f7a43c7c6ef8563d0ebdd4a3b496ac",
                 account_id="001-004-2840244-004",
                 environment="live")
    params = {
        "granularity": 'D',
        "from": start_date,
        "to": end_date
    }

    for ticker in tickers:
        print(ticker['source_ticker'], ticker['inst_code'])
        response = o.candle_data(instrument=ticker['source_ticker'],
                                 params=params)['candles']

        for data in response:
            date = datetime.strptime(data['time'][0:10], "%Y-%m-%d") + timedelta(days=1)
            print(date, data['mid']['c'])

            try:
                price = Prices.objects.get(date=date,
                                           inst_code=int(ticker['inst_code']))
                price.price = float(data['mid']['c'])
                price.save()
            except:
                Prices(date=date,
                       inst_code=int(ticker['inst_code']),
                       price=float(data['mid']['c']),
                       source='oanda'
                       ).save()
    return ''