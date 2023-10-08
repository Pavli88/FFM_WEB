from portfolio.models import Transaction, TransactionPnl, Holding, Nav, Portfolio
from instrument.models import Instruments, Prices
import pandas as pd
from datetime import datetime
from datetime import date
from django.db import connection
from datetime import timedelta
from django.db.models import Q


def calculate_transaction_pnl(transaction_id):
    print("TRANSACTION PROFIT CALC")
    print(transaction_id)
    cursor = connection.cursor()
    cursor.execute(
        """select*from portfolio_transaction
       where transaction_link_code in (select id from portfolio_transaction where transaction_link_code={id})
          or transaction_link_code={id}
          or id={id};""".format(id=transaction_id)
    )
    row = cursor.fetchall()
    df = pd.DataFrame(row, columns=[col[0] for col in cursor.description])
    main_transaction = Transaction.objects.get(id=transaction_id)
    if main_transaction.sec_group == 'CFD':
        margin_sum = df[df['sec_group'] == 'Margin']['mv'].sum()
        cash_sum = df[df['sec_group'] == 'Cash']['mv'].sum()
        pnl = margin_sum * -1 + cash_sum
    else:
        pnl = df[df['sec_group'] == 'Cash']['mv'].sum()
    try:
        transaction_pnl = TransactionPnl.objects.get(transaction_id=transaction_id,
                                                     portfolio_code=main_transaction.portfolio_code)
        transaction_pnl.pnl = pnl
        transaction_pnl.save()
    except:
        TransactionPnl(
            transaction_id=transaction_id,
            portfolio_code=main_transaction.portfolio_code,
            security=main_transaction.security,
            pnl=pnl).save()


def cumulative_return_calc(data_series):
    return_list = [100]
    for record in enumerate(data_series):
        if record[0] == 0:
            return_record = return_list[-1]*((record[1]*100/100)+1)
        else:
            return_record = return_list[-1]*((record[1]*100/100)+1)
        return_list.append(round(return_record, 3))
    return return_list


def drawdown_calc(data_series):
    cum_ret_series = cumulative_return_calc(data_series=data_series)
    drawdown_list = []
    for record in enumerate(cum_ret_series):
        try:
            series_max = max(cum_ret_series[0: record[0]])
            if record[1] > series_max:
                drawdown_list.append(0)
            else:
                drawdown_list.append(round(((record[1]/series_max)-1)*100, 2))
        except:
            pass
    return drawdown_list

