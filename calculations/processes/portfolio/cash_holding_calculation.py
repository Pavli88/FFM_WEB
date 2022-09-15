from portfolio.models import *
from mysite.models import Exceptions
from calculations.models import PortfolioProcessStatus

import pandas as pd
import datetime
import numpy as np
from datetime import timedelta
from mysite.my_functions.general_functions import *
from django.db import connection


def cash_holding_calculation(portfolio_code, start_date, end_date):
    port_data = Portfolio.objects.filter(portfolio_code=portfolio_code).values()
    print(port_data)
    inception_date = port_data[0]['inception_date']
    print('INCEPTION DATE', inception_date)
    print('START DATE', start_date)

    if start_date < inception_date:
        start_date = inception_date
    print('UPDATED INCEP DATE', start_date)
    cursor = connection.cursor()
    query = """select pt.portfolio_code, pt.mv, pt.date, pt.transaction_type, inst.inst_code, inst.currency
from portfolio_trade as pt, instrument_instruments as inst
where pt.security = inst.id
and (pt.transaction_type = 'fee'
    or pt.transaction_type = 'cash deposit'
    or pt.transaction_type = 'cash withdrawal'
    or pt.transaction_type = 'income'
    or pt.transaction_type = 'dividend'
    or pt.transaction_type = 'trading cost'
    or pt.transaction_type = 'sale settlement'
    or pt.transaction_type = 'purchase settlement')
and pt.portfolio_code='{portfolio_code}'
and pt.date >= '{start_date}';""".format(portfolio_code=portfolio_code, start_date=start_date)
    cursor.execute(query)
    transactions_df = pd.DataFrame(cursor.fetchall()).rename(columns={0: 'portfolio_code',
                                                         1: 'market_value',
                                                         2: 'date',
                                                         3: 'transaction_type',
                                                         4: 'security_code',
                                                         5: 'currency'})

    initial_cash_holdins = pd.DataFrame(CashHolding.objects.filter(date=start_date, portfolio_code=portfolio_code).values())
    starting_df = initial_cash_holdins.pivot(columns='currency', values=['amount'], index='date').reset_index()
    starting_df.columns = ['date'] + initial_cash_holdins['currency'].values.tolist()
    print('initial cash holding df')
    print(initial_cash_holdins)
    print('starting df')
    print(starting_df)
    print('TRANSACTIONS FOR THE PERIOD')
    print(transactions_df)
    if transactions_df.empty:
        currencies = list(dict.fromkeys(list(initial_cash_holdins['currency'])))
        tf = starting_df
    else:
        currencies = list(dict.fromkeys(list(transactions_df['currency']) + list(initial_cash_holdins['currency'])))
        tf = transactions_df.groupby(['date', 'currency']).sum().reset_index().pivot(columns='currency', values=['market_value'], index='date').fillna(0).reset_index()
    print('FORMATED AGGREGATED DF')
    print(tf)
    column_values = ['date'] + [col[1] for col in tf.columns[1:]]
    # tf.columns = column_values
    dates_list = tf['date'].values.tolist()
    zero_list = [0 for i in currencies]
    data = []

    while start_date <= end_date:
        if start_date in dates_list:
            pass
        else:
            data.append([start_date] + zero_list)
        start_date = start_date + timedelta(days=1)
    final_df = pd.DataFrame(data + tf.values.tolist(), columns=column_values).sort_values(by=['date']).fillna(0)
    print(final_df)
    for currency in currencies:
        final_df[currency] = final_df[currency].cumsum()
    # print(currencies)
    # print(transactions_df)
    # print(transactions_df.groupby(['date', 'currency']).sum())
    # print(tf['date'])
    # print(tf)
    # print(final_df)
    # print(zero_list)

    return final_df