from portfolio.models import Transaction, TransactionPnl, CashHolding, Holding, Nav
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


def date_wrapper():
    while calculation_date <= date.today():
        calculation_date = calculation_date + timedelta(days=1)


def calculate_holdings(portfolio_code, calc_date):
    calc_date = datetime.strptime(str(calc_date), '%Y-%m-%d').date()
    previous_date = calc_date - timedelta(days=1)

    print(portfolio_code, calc_date, previous_date)

    # Previous holding data
    try:
        previous_holding = pd.read_json(Holding.objects.get(date=previous_date, portfolio_code=portfolio_code).data)
        previous_assets_list = previous_holding[previous_holding['ending_pos'] != 0.0]['id'].tolist()
    except Holding.DoesNotExist:
        print("Previous holding does not exists")
        previous_holding = pd.DataFrame({})
        previous_assets_list = []
    print('PREVIOUS HOLDING')
    print(previous_holding)
    print('')

    # Current transactions
    current_transactions = pd.DataFrame(Transaction.objects.filter(portfolio_code=portfolio_code, trade_date=calc_date).values())
    print(len(current_transactions))
    print('TRANSACTIONS')
    print(current_transactions)
    print('')

    # Asset List
    print('Previous Assets List', previous_assets_list)
    if len(current_transactions) == 0:
        current_assets_list = []
        leverages = []
    else:
        current_assets_list = current_transactions['security'].tolist()
        leverages = current_transactions[current_transactions['sec_group'] == 'CFD'].groupby('currency')['margin_balance'].sum().reset_index()

    if len(leverages) > 0:
        leverage_assets_list = list(Instruments.objects.filter(type='Leverage', currency__in=list(leverages['currency'])).values_list('id', flat=True))
    else:
        leverage_assets_list = []

    print('')
    print('LEVERAGES')
    print(leverages)
    print(leverage_assets_list)
    print('')

    print('Current Assets', current_assets_list)
    all_assests_list = list(dict.fromkeys(previous_assets_list + current_assets_list + leverage_assets_list))
    print('ALL ASSETS LIST', all_assests_list)

    # Fetching prices
    prices_df = pd.DataFrame(Prices.objects.filter(inst_code__in=all_assests_list, date=calc_date).values())
    print('')
    print('PRICES')
    print(prices_df)
    print('')

    # Fetching instrument data from database
    all_assets_df = pd.DataFrame(Instruments.objects.filter(id__in=all_assests_list).values())

    beginning_positions = []
    beginning_mvs = []
    ending_positions = []
    pos_movement = []
    prices = []
    ending_mvs = []
    for index, row in all_assets_df.iterrows():
        print('---', row['id'], row['type'], row['currency'])

        try:
            beginning_position = previous_holding[previous_holding['id'] == row['id']]['ending_pos'].tolist()[0]
            print('BEG POS')
            print(beginning_position)
            print('')
        except:
            beginning_position = 0.0
        beginning_positions.append(beginning_position)

        try:
            beginning_mv = previous_holding[previous_holding['id'] == row['id']]['ending_mv'].tolist()[0]
            print('BEG MV')
            print(beginning_mv)
            print('')
        except:
            beginning_mv = 0.0
        beginning_mvs.append(beginning_mv)

        try:
            print(len(current_transactions))
            if len(current_transactions) == 0:
                ending_position = beginning_position
            else:
                ending_position = beginning_position + current_transactions[current_transactions['security'] == row['id']]['quantity'].sum()
                if row['type'] == 'Cash':
                    trade_cf = current_transactions[(current_transactions['currency'] == row['currency']) & (current_transactions['sec_group'] != 'Cash')]['net_cashflow'].sum()
                    ending_position = ending_position + trade_cf
                    print('TRADE CF')
                    print(trade_cf)
                    print('')
                elif row['type'] == 'Leverage':
                    leverage = list(leverages[leverages['currency'] == row['currency']]['margin_balance'])[0]
                    ending_position = ending_position + leverage

            print('CURRENT POS')
            print(ending_position)
            print('')
        except:
            ending_position = 0.0

        try:
            if row['type'] == 'Cash' or row['type'] == 'Leverage':
                price = 1
            else:
                price = float(list(prices_df[prices_df['inst_code'] == str(row['id'])]['price'])[0])
        except:
            print('Price is missing for date')

        ending_mvs.append(ending_position * price)
        prices.append(price)
        ending_positions.append(ending_position)
        pos_movement.append(float(ending_position) - float(beginning_position))

    all_assets_df['beginning_pos'] = beginning_positions
    all_assets_df['ending_pos'] = ending_positions
    all_assets_df['pos_movement'] = pos_movement
    all_assets_df['price'] = prices
    all_assets_df['beginning_mv'] = beginning_mvs
    all_assets_df['ending_mv'] = ending_mvs
    total_mv = all_assets_df['ending_mv'].sum()
    all_assets_df['weights'] = all_assets_df['ending_mv'] / total_mv
    print(total_mv)
    print(all_assets_df)

    try:
        holding = Holding.objects.get(date=calc_date, portfolio_code=portfolio_code)
        holding.data = all_assets_df.to_json()
        holding.save()
        print("Holding exists")
    except:
        print("Holding does not exist")
        Holding(date=calc_date,
                portfolio_code=portfolio_code,
                data=all_assets_df.to_json()).save()


    asset_val = all_assets_df[(all_assets_df['type'] != 'Cash') & (all_assets_df['type'] != 'Leverage')]['ending_mv'].sum()
    total_cash = all_assets_df[all_assets_df['type'] == 'Cash']['ending_mv'].sum()
    short_liab = all_assets_df[all_assets_df['type'] == 'Leverage']['ending_mv'].sum()
    total = asset_val + total_cash - short_liab
    try:
        nav = Nav.objects.get(date=calc_date, portfolio_code=portfolio_code)
        nav.cash_val = total_cash
        nav.pos_val = asset_val
        nav.short_liab = short_liab
        nav.total = total
        nav.save()
    except:
        Nav(date=calc_date,
            portfolio_code=portfolio_code,
            pos_val=asset_val,
            cash_val=total_cash,
            short_liab=short_liab,
            total=total).save()
