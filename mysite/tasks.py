from celery import shared_task
import time
from django.utils.timezone import now
import json
from broker_apis.oanda import OandaV20
from instrument.models import Tickers, Prices
from datetime import datetime, timedelta
from accounts.models import BrokerAccounts
from calculations.processes.valuation.valuation import calculate_holdings


@shared_task
def long_running_task():
    print("TEST TASK")
    time.sleep(10)  # Simulating a long-running task
    return "Task Complete!"

@shared_task
def valuation():
    calculate_holdings(portfolio_code="SO1", calc_date="2025-02-19")
    return "Valuation Complete!"

@shared_task
def oanda_pricing(start_date, end_date):
    tickers = Tickers.objects.filter(source='oanda').values()
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
        print(ticker['source_ticker'], ticker['inst_code'])
        response = o.candle_data(instrument=ticker['source_ticker'],
                                 params=params)['candles']

        for data in response:
            date = datetime.strptime(data['time'][0:10], "%Y-%m-%d") + timedelta(days=1)
            print(date, data['mid']['c'])

            try:
                price = Prices.objects.get(date=date,
                                           instrument_id=int(ticker['inst_code']))
                price.price = float(data['mid']['c'])
                price.save()
            except:
                Prices(date=date,
                       instrument_id=int(ticker['inst_code']),
                       price=float(data['mid']['c']),
                       source='oanda'
                       ).save()
    return ''