from portfolio.models import *
from mysite.models import Exceptions
from calculations.models import PortfolioProcessStatus

import pandas as pd
import datetime
import numpy as np
from datetime import timedelta
from mysite.my_functions.general_functions import *
from django.db import connection


def cash_holding_calculation(portfolio_code, calc_date):
    date = datetime.datetime.strptime(str(calc_date), '%Y-%m-%d')
    curent_date = get_today()
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
and pt.date = '{start_date}';""".format(portfolio_code=portfolio_code, start_date=date)

    cursor.execute(query)
    df = pd.DataFrame(cursor.fetchall()).rename(columns={0: 'portfolio_code',
                                                         1: 'market_value',
                                                         2: 'date',
                                                         3: 'transaction_type',
                                                         4: 'security_code',
                                                         5: 'currency'})

    # Previous day cash holdings
    t_min_one_cash_holdings = pd.DataFrame(CashHolding.objects.filter(date=previous_business_day(str(calc_date))).filter(portfolio_code=portfolio_code).values())

    # print(df)
    # print(t_min_one_cash_holdings)

    if df.empty and t_min_one_cash_holdings.empty:
        print('empty df')
        try:
            existing_exception = Exceptions.objects.get(entity_code=portfolio_code,
                                                        exception_type='No Previous Day Calculation',
                                                        calculation_date=calc_date)
            existing_exception.status = 'Error'
            existing_exception.save()
        except Exceptions.DoesNotExist:
            Exceptions(exception_level='Portfolio',
                       entity_code=portfolio_code,
                       exception_type='No Previous Day Calculation',
                       process='Cash Holding',
                       status='Error',
                       creation_date=datetime.datetime.now(),
                       calculation_date=calc_date).save()
        try:
            portfolio_process_status = PortfolioProcessStatus.objects.get(date=calc_date,
                                                                          portfolio_code=portfolio_code)
            portfolio_process_status.cash_holding = 'Error'
            portfolio_process_status.save()
        except PortfolioProcessStatus.DoesNotExist:
            PortfolioProcessStatus(date=calc_date,
                                   portfolio_code=portfolio_code,
                                   cash_holding='Error').save()
    else:
        print(t_min_one_cash_holdings)
    # currencies = list(dict.fromkeys(list(df['currency'])))
    # print(currencies)

    # for currency in currencies:
    #     beginning_date = start_date
    #     currency_df = df[df['currency'] == currency]
    #     while beginning_date <= curent_date:
    #
    #         # Current days values
    #         try:
    #             filtered_df = currency_df[currency_df['date'] == beginning_date].groupby(['date']).sum()
    #             current_cash_value = filtered_df['market_value'][0]
    #         except:
    #             current_cash_value = 0.0
    #             try:
    #                 existing_exception = Exceptions.objects.get(entity_code=portfolio_code,
    #                                                             exception_type='Zero Cash Movement',
    #                                                             security_id=currency,
    #                                                             calculation_date=beginning_date)
    #                 existing_exception.status = 'Alert'
    #                 existing_exception.save()
    #             except Exceptions.DoesNotExist:
    #                 Exceptions(exception_level='Security',
    #                            entity_code=portfolio_code,
    #                            exception_type='Zero Cash Movement',
    #                            process='Cash Holding',
    #                            status='Alert',
    #                            security_id=currency,
    #                            creation_date=datetime.datetime.now(),
    #                            calculation_date=beginning_date).save()
    #
    #         # Previous days values
    #         t_min_one_cash_holding = CashHolding.objects.filter(date=previous_business_day(str(beginning_date))).filter(
    #             currency=currency).filter(portfolio_code=portfolio_code).values()
    #         if len(t_min_one_cash_holding) == 0:
    #             previous_cash_value = 0.0
    #         else:
    #             previous_cash_value = t_min_one_cash_holding[0]['amount']
    #
    #         # Calculating total cash values based on current day and previous day s values
    #         total_cash_value = current_cash_value + previous_cash_value
    #
    #         # Writing cash record to database
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
    try:
        portfolio_process_status = PortfolioProcessStatus.objects.get(date=calc_date,
                                                                      portfolio_code=portfolio_code)
        portfolio_process_status.cash_holding = 'Completed'
        portfolio_process_status.save()
    except PortfolioProcessStatus.DoesNotExist:
        PortfolioProcessStatus(date=calc_date,
                               portfolio_code=portfolio_code,
                               cash_holding='Completed').save()
    return 'test'