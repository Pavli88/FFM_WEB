from portfolio.models import Transaction, TransactionPnl, CashHolding
import pandas as pd
from datetime import datetime
from datetime import date
from django.db import connection
from datetime import timedelta


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


def calculate_cash_holding(portfolio_code, start_date, currency):
    start_date = datetime.strptime(str(start_date), '%Y-%m-%d').date()

    # Only cash transactions
    # cash_transactions = pd.DataFrame(Transaction.objects.filter(trade_date__gte=start_date,
    #                                                             portfolio_code=portfolio_code,
    #                                                             currency=currency,
    #                                                             sec_group='Cash').values())
    cursor = connection.cursor()
    cursor.execute(
        """
        select sum(mv) as mv, trade_date from portfolio_transaction
       where trade_date >='{trade_date}'
       and portfolio_code='{portfolio_code}'
       and currency='{currency}'
and transaction_type='Subscription'
or transaction_type='Redemption'
or transaction_type='Interest Received'
or transaction_type='Dividend'
or transaction_type='Interest Paid'
or transaction_type='Commission'
group by trade_date;
        """.format(trade_date=start_date,
                   currency=currency,
                   portfolio_code=portfolio_code)
    )
    row = cursor.fetchall()
    cash_df = pd.DataFrame(row, columns=[col[0] for col in cursor.description])
    print(cash_df)


    # Open transactions cashflow
    cursor = connection.cursor()
    cursor.execute(
        """
        select id, mv as mv, trade_date
from portfolio_transaction
where transaction_link_code in (select id
                                from portfolio_transaction
                                where open_status = 'Open'
                                  and trade_date >= '{trade_date}'
                                  and currency = '{currency}'
                                  and portfolio_code = '{portfolio_code}')
  and sec_group = 'Cash';
        """.format(trade_date=start_date,
                   currency=currency,
                   portfolio_code=portfolio_code)
    )
    row = cursor.fetchall()
    open_df = pd.DataFrame(row, columns=[col[0] for col in cursor.description])
    print(open_df)
    # Closed transaction

    # Starting balance
    try:
        cumulative_cash_value = CashHolding.objects.filter(date__lt=start_date,
                                                           currency=currency,
                                                           portfolio_code=portfolio_code).order_by('date').latest('date').amount
    except:
        cumulative_cash_value = 0.0
    calculation_date = start_date

    while calculation_date <= date.today():
        if len(open_df[open_df['trade_date'] == calculation_date]) == 0:
            open_transactions = 0.0
        else:
            open_transactions = open_df[open_df['trade_date'] == calculation_date]['mv'].sum()

        if len(cash_df[cash_df['trade_date'] == calculation_date]) == 0:
            cash_transactions = 0.0
        else:
            cash_transactions = list(cash_df[cash_df['trade_date'] == calculation_date]['mv'])[0]

        cumulative_cash_value = cumulative_cash_value + cash_transactions + open_transactions
        print(calculation_date, cumulative_cash_value)
        try:
            existing_cash_record = CashHolding.objects.get(portfolio_code=portfolio_code,
                                                           currency=currency,
                                                           date=calculation_date)
            existing_cash_record.amount = cumulative_cash_value
            existing_cash_record.save()
        except CashHolding.DoesNotExist:
            CashHolding(portfolio_code=portfolio_code,
                        currency=currency,
                        amount=cumulative_cash_value,
                        date=calculation_date).save()
        calculation_date = calculation_date + timedelta(days=1)


def calculate_nav(portfolio_code, calc_date):
    print(portfolio_code, calc_date)