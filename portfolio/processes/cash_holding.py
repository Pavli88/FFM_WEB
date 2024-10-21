from portfolio.models import *
import pandas as pd
import datetime
import numpy as np
from datetime import timedelta
from mysite.my_functions.general_functions import *
from django.db import connection


def cash_holding(portfolio_code, calc_date):
    date = datetime.datetime.strptime(str(calc_date), '%Y-%m-%d')
    curent_date = get_today()
    cash_transactions = Transaction.objects.filter(trade_date__gte=date).values()
    print(cash_transactions)
#     cursor = connection.cursor()
#     query = """select pt.portfolio_code, pt.mv, pt.date, pt.transaction_type, inst.inst_code, inst.currency
# from portfolio_trade as pt, instrument_instruments as inst
# where pt.security = inst.id
# and (pt.transaction_type = 'fee'
#     or pt.transaction_type = 'cash deposit'
#     or pt.transaction_type = 'cash withdrawal'
#     or pt.transaction_type = 'income'
#     or pt.transaction_type = 'dividend'
#     or pt.transaction_type = 'trading cost'
#     or pt.transaction_type = 'sale settlement'
#     or pt.transaction_type = 'purchase settlement')
# and pt.portfolio_code='{portfolio_code}'
# and pt.date >= '{start_date}';""".format(portfolio_code=portfolio_code, start_date=date)
#
#     cursor.execute(query)
#     df = pd.DataFrame(cursor.fetchall()).rename(columns={0: 'portfolio_code',
#                                                          1: 'market_value',
#                                                          2: 'date',
#                                                          3: 'transaction_type',
#                                                          4: 'security_code',
#                                                          5: 'currency'})
#     print(df)
#     currencies = list(dict.fromkeys(list(df['currency'])))
#     print(currencies)
    # for currency in currencies:
    #     beginning_date = start_date
    #     currency_df = df[df['currency'] == currency]
    #     while beginning_date <= curent_date:
    #         try:
    #             filtered_df = currency_df[currency_df['date'] == beginning_date].groupby(['date']).sum()
    #             current_cash_value = filtered_df['market_value'][0]
    #         except:
    #             current_cash_value = 0.0
    #         t_min_one_cash_holding = CashHolding.objects.filter(date=previous_business_day(str(beginning_date))).filter(
    #             currency=currency).filter(portfolio_code=portfolio_code).values()
    #
    #         if len(t_min_one_cash_holding) == 0:
    #             previous_cash_value = 0.0
    #         else:
    #             previous_cash_value = t_min_one_cash_holding[0]['amount']
    #         total_cash_value = current_cash_value + previous_cash_value
    #         try:
    #             existing_cash_record = CashHolding.objects.get(portfolio_code=portfolio_code,
    #                                                            currency=currency,
    #                                                            date=beginning_date)
    #             existing_cash_record.amount = total_cash_value
    #             existing_cash_record.save()
    #             print(existing_cash_record)
    #         except CashHolding.DoesNotExist:
    #             print('record doesnot exist')
    #             CashHolding(portfolio_code=portfolio_code,
    #                         currency=currency,
    #                         amount=total_cash_value,
    #                         date=beginning_date).save()
    #         beginning_date = beginning_date + timedelta(days=1)
    return 'test'