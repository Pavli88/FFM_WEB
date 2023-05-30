from portfolio.models import Transaction, TransactionPnl, CashHolding, Holding, Nav, Portfolio
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
                                                           portfolio_code=portfolio_code).order_by('date').latest(
            'date').amount
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
    portfolio_data = Portfolio.objects.get(portfolio_code=portfolio_code)
    portfolio_currency = Instruments.objects.get(currency=portfolio_data.currency,
                                                 group='Cash')
    leverage_instrument = Instruments.objects.get(currency=portfolio_data.currency,
                                                  type='Leverage')
    while calc_date <= date.today():
        holding_df = pd.DataFrame({'transaction_id': [],
                                   'instrument_name': [],
                                   'instrument_id': [],
                                   'group': [],
                                   'type': [],
                                   'currency': [],
                                   'trade_date': [],
                                   'transaction_type': [],
                                   'beginning_pos': [],
                                   'ending_pos': [],
                                   'change': [],
                                   'trade_price': [],
                                   'valuation_price': [],
                                   'beginning_mv': [],
                                   'ending_mv': [],
                                   })

        if portfolio_data.weekend_valuation is False and (calc_date.weekday() == 6 or calc_date.weekday() == 5):
            print('---', calc_date, calc_date.strftime('%A'), 'Not calculate')
        else:
            if portfolio_data.weekend_valuation is False and calc_date.weekday() == 0:
                time_back = 3
            else:
                time_back = 1
            previous_date = calc_date - timedelta(days=time_back)

            print('---------------PERIOD--------------', calc_date)

            # Previous holding data
            try:
                previous_holding = pd.read_json(
                    Holding.objects.get(date=previous_date, portfolio_code=portfolio_code).data)
                # previous_assets_list = previous_holding[previous_holding['ending_pos'] != 0.0]['id'].tolist()
            except Holding.DoesNotExist:
                previous_holding = pd.DataFrame({})
                # previous_assets_list = []

            # Current transactions
            cursor = connection.cursor()
            cursor.execute(
                """
                select*from portfolio_transaction as pt, instrument_instruments as inst
where pt.security = inst.id
and pt.portfolio_code = '{portfolio_code}'
and pt.trade_date = '{trade_date}'
                """.format(trade_date=calc_date,
                           portfolio_code=portfolio_code)
            )
            current_transactions = cursor.fetchall()
            current_transactions_df = pd.DataFrame(current_transactions, columns=[col[0] for col in cursor.description])

            # Assets
            try:
                current_assets_df = current_transactions_df[(current_transactions_df['sec_group'] != 'Cash') & (current_transactions_df['transaction_link_code'] == 0)]
            except:
                current_assets_df = []

            try:
                linked_assets_df = current_transactions_df[(current_transactions_df['sec_group'] != 'Cash') & (current_transactions_df['transaction_link_code'] != 0)]
            except:
                linked_assets_df = []

            # ASSET VALUATION
            if len(previous_holding) > 0:
                previous_assets_df = previous_holding[(previous_holding['type'] != 'Cash') & (previous_holding['type'] != 'Leverage')]
                # Valuation of existing positions
                for index, row in previous_assets_df.iterrows():
                    if row['ending_pos'] > 0:
                        linked_quantity = current_transactions_df[current_transactions_df['transaction_link_code'] == row['transaction_id']][
                                'quantity'].sum()
                        holding_df.loc[len(holding_df.index)] = [
                            row['transaction_id'],
                            row['instrument_name'],
                            row['instrument_id'],
                            row['group'],
                            row['type'],
                            row['currency'],
                            str(row['trade_date']),
                            row['transaction_type'],
                            row['ending_pos'],
                            row['ending_pos'] + linked_quantity,
                            (row['ending_pos'] + linked_quantity) - row['ending_pos'],
                            row['trade_price'],
                            1,
                            row['ending_mv'],
                            0,
                        ]

            if len(current_assets_df) > 0:
                for index, row in current_assets_df.iterrows():
                    # Filtering for linked transactions
                    try:
                        linked_quantity = current_transactions_df[current_transactions_df['transaction_link_code'] == row['id'][0]][
                            'quantity'].sum()
                    except:
                        linked_quantity = 0.0
                    holding_df.loc[len(holding_df.index)] = [
                        row['id'][0],
                        row['name'],
                        row['security'],
                        row['group'],
                        row['type'],
                        row['currency'][0],
                        str(calc_date),
                        row['transaction_type'],
                        0,
                        row['quantity'] + linked_quantity,
                        0,
                        row['price'],
                        1,
                        0,
                        0,
                    ]
            holding_df = holding_df.sort_values('instrument_name')

            # PRICING OF ASSETS
            intrument_list = list(dict.fromkeys(holding_df['instrument_id']))
            prices_df = pd.DataFrame(Prices.objects.filter(date=calc_date, inst_code__in=intrument_list).values())

            for index, row in holding_df.iterrows():
                try:
                    price = list(prices_df[prices_df['inst_code'] == row['instrument_id']]['price'])[0]
                    holding_df.loc[index, ['valuation_price']] = price
                    holding_df.loc[index, ['ending_mv']] = price * row['ending_pos']
                except:
                    return 'Price is missing for ' + row['instrument_name'] + ' on ' + str(calc_date)

            if len(holding_df) > 0:
                asset_val = holding_df['ending_mv'].sum()

                if len(previous_holding) > 0:
                    previous_levereage = previous_holding[previous_holding['instrument_id'] == leverage_instrument.id]['ending_mv'].sum()
                else:
                    print('No previous leverage')
                    previous_levereage = 0.0

                if len(current_assets_df) > 0:
                    current_levereage = current_assets_df['margin_balance'].sum()
                else:
                    print('no current leverage')
                    current_levereage = 0.0

                if len(linked_assets_df) > 0:
                    linked_leverage = linked_assets_df['margin_balance'].sum()
                else:
                    linked_leverage = 0.0

                total_leverage = previous_levereage + current_levereage + linked_leverage

                # Leverage
                holding_df.loc[len(holding_df.index)] = [
                    leverage_instrument.id,
                    leverage_instrument.name,
                    leverage_instrument.id,
                    leverage_instrument.group,
                    leverage_instrument.type,
                    leverage_instrument.currency,
                    str(calc_date),
                    '-',
                    previous_levereage,
                    total_leverage,
                    total_leverage-previous_levereage,
                    1,
                    1,
                    previous_levereage,
                    total_leverage,
                ]
                short_liab = total_leverage
            else:
                asset_val = 0.0
                short_liab = 0.0

            # CASH CALCULATION
            # CASH TRANSACTIONS + CURRENT TRADE CF + PREVIOUS TOTAL CF
            if len(current_transactions_df) > 0:
                total_cash_transactions = current_transactions_df[current_transactions_df['sec_group'] == 'Cash']['mv'].sum()
            else:
                total_cash_transactions = 0.0

            if len(current_assets_df) > 0:
                current_trade_cash = current_assets_df['net_cashflow'].sum()
            else:
                current_trade_cash = 0.0

            if len(previous_holding) > 0:
                previous_total_cash = list(previous_holding[previous_holding['type'] == 'Cash']['ending_mv'])[0]
            else:
                previous_total_cash = 0.0

            if len(linked_assets_df) > 0:
                linked_cash = linked_assets_df['net_cashflow'].sum()
            else:
                linked_cash = 0.0

            total_cash = total_cash_transactions + current_trade_cash + previous_total_cash + linked_cash
            holding_df.loc[len(holding_df.index)] = [
                portfolio_currency.id,
                portfolio_currency.name,
                portfolio_currency.id,
                portfolio_currency.group,
                portfolio_currency.type,
                portfolio_currency.currency,
                str(calc_date),
                '-',
                round(previous_total_cash, 5),
                round(total_cash, 5),
                round(total_cash - previous_total_cash, 5),
                1,
                1,
                previous_total_cash,
                total_cash,
            ]

            print('FINAl REPORT')
            holding_df = holding_df[holding_df.ending_pos != 0]
            print(holding_df)

            try:
                holding = Holding.objects.get(date=calc_date, portfolio_code=portfolio_code)
                holding.data = holding_df.to_json()
                holding.save()
            except:
                Holding(date=calc_date,
                        portfolio_code=portfolio_code,
                        data=holding_df.to_json()).save()

            # # Saving NAV
            total_cash = total_cash
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

        calc_date = calc_date + timedelta(days=1)
    return 'Valuation is completed.'
