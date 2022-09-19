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
    calc_start_date = previous_month_end(current_day=start_date)
    print('REQUEST DATE', start_date)
    print('PREVIOUS MONTH END', calc_start_date)
    port_data = Portfolio.objects.filter(portfolio_code=portfolio_code).values()
    inception_date = port_data[0]['inception_date']
    if calc_start_date < inception_date:
        calc_start_date = inception_date

    print('INCEPTION DATE', inception_date)
    print('FROM DATE', calc_start_date)

    # Fetching transactions from the from date
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
and pt.date >= '{start_date}';""".format(portfolio_code=portfolio_code, start_date=calc_start_date)
    cursor.execute(query)
    transactions_df = pd.DataFrame(cursor.fetchall()).rename(columns={0: 'portfolio_code',
                                                         1: 'market_value',
                                                         2: 'date',
                                                         3: 'transaction_type',
                                                         4: 'security_code',
                                                         5: 'currency'})

    # Fetching the cash balance for the from date
    initial_cash_holdings = pd.DataFrame(CashHolding.objects.filter(date=calc_start_date, portfolio_code=portfolio_code).values())
    print('')
    print('FROM DATE CASH BALANCE')
    print(initial_cash_holdings)
    if initial_cash_holdings.empty:
        print('START DATE BALANCE IS MISSING')
        return ''
    starting_df = initial_cash_holdings.pivot(columns='currency', values=['amount'], index='date').reset_index()
    starting_df.columns = ['date'] + initial_cash_holdings['currency'].values.tolist()

    print('')
    print('starting df')
    print(starting_df)
    print('')
    print('TRANSACTIONS FOR THE PERIOD')
    print(transactions_df)
    if transactions_df.empty:
        currencies = list(dict.fromkeys(list(initial_cash_holdings['currency'])))
        tf = starting_df
        column_values = tf.columns
    else:
        currencies = list(dict.fromkeys(list(transactions_df['currency']) + list(initial_cash_holdings['currency'])))
        tf = transactions_df.groupby(['date', 'currency']).sum().reset_index().pivot(columns='currency', values=['market_value'], index='date').fillna(0).reset_index()
        column_values = ['date'] + [col[1] for col in tf.columns[1:]]

    print('FORMATED AGGREGATED DF')
    print(tf)
    print(tf.columns)
    print(column_values)
    # tf.columns = column_values
    dates_list = tf['date'].values.tolist()
    zero_list = [0 for i in currencies]
    data = []

    while calc_start_date <= end_date:
        if calc_start_date in dates_list:
            pass
        else:
            data.append([calc_start_date] + zero_list)
        calc_start_date = calc_start_date + timedelta(days=1)
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
    # Writing cash balance at monthd end to database
    for index, row in final_df.reset_index().iterrows():
        if row['date'].day == 1:
            print('First day of month')
            month_end_cash_balances = final_df.loc[[index-1]]
            print(month_end_cash_balances)
            for column in month_end_cash_balances:
                if column != 'date':
                    print(month_end_cash_balances[column])

            # try:
            #     existing_cash_record = CashHolding.objects.get(portfolio_code=portfolio_code,
            #                                                    currency=currency,
            #                                                    date=beginning_date)
            #     existing_cash_record.amount = total_cash_value
            #     existing_cash_record.save()
            #     print(existing_cash_record)
            # except CashHolding.DoesNotExist:
            #     print('record doesnot exist')
            #     CashHolding(portfolio_code=portfolio_code,
            #                 currency=currency,
            #                 amount=total_cash_value,
            #                 date=beginning_date).save()

            try:
                existing_process_record = PortfolioProcessStatus.objects.get(date=month_end_cash_balances['date'].values.tolist()[0],
                                                                             portfolio_code=portfolio_code)
                existing_process_record.cash_holding = 'Calculated'
                existing_process_record.save()
            except PortfolioProcessStatus.DoesNotExist:
                PortfolioProcessStatus(date=month_end_cash_balances['date'].values.tolist()[0],
                                       portfolio_code=portfolio_code,
                                       cash_holding='Calculated').save()

    print(portfolio_code)

    return final_df