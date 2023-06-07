from portfolio.models import Transaction, TransactionPnl, CashHolding, Holding, Nav, Portfolio
from instrument.models import Instruments, Prices
import pandas as pd
from datetime import datetime
from datetime import date
from django.db import connection
from datetime import timedelta


def calculate_holdings(portfolio_code, calc_date):
    calc_date = datetime.strptime(str(calc_date), '%Y-%m-%d').date()
    portfolio_data = Portfolio.objects.get(portfolio_code=portfolio_code)
    portfolio_currency = Instruments.objects.get(currency=portfolio_data.currency,
                                                 group='Cash')
    leverage_instrument = Instruments.objects.get(currency=portfolio_data.currency,
                                                  type='Leverage')
    print('INCEPTION_DATE', portfolio_data.inception_date)
    response_list = []
    error_list = []

    if portfolio_data.status == 'Not Funded':
        error_list.append({'portfolio_code': portfolio_code,
                           'date': calc_date,
                           'process': 'Valuation',
                           'exception': 'Not Funded',
                           'status': 'Error',
                           'comment': 'Portfolio is not funded. Valuation is not possible'})
        return response_list + error_list

    while calc_date <= date.today():
        if calc_date < portfolio_data.inception_date:
            response_list.append({'portfolio_code': portfolio_code,
                                  'date': calc_date,
                                  'process': 'Valuation',
                                  'exception': '-',
                                  'status': 'Alert',
                                  'comment': str(calc_date) + ' is lett than inception date.'})
        else:
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
                                       'pnl': []
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
                                0,
                                row['trade_price'],
                                1,
                                row['ending_mv'],
                                0,
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
                            0,
                        ]
                holding_df = holding_df.sort_values('instrument_name')
                holding_df['change'] = holding_df['ending_pos'] - holding_df['beginning_pos']
                # PRICING OF ASSETS
                intrument_list = list(dict.fromkeys(holding_df['instrument_id']))
                prices_df = pd.DataFrame(Prices.objects.filter(date=calc_date, inst_code__in=intrument_list).values())
                print(intrument_list)
                print(prices_df)

                for inst in intrument_list:
                    try:
                        prices_df[prices_df['inst_code'] == inst]
                    except:
                        error_list.append({'portfolio_code': portfolio_code,
                                              'date': calc_date,
                                              'process': 'Valuation',
                                              'exception': 'Missing Price',
                                              'status': 'Error',
                                              'comment': 'Security Code: ' + str(inst)})

                for index, row in holding_df.iterrows():
                    try:
                        price = list(prices_df[prices_df['inst_code'] == row['instrument_id']]['price'])[0]
                        holding_df.loc[index, ['valuation_price']] = price
                        if row['transaction_type'] == 'Sale' and row['group'] == 'CFD':
                            pnl = (row['trade_price'] - price) * row['ending_pos']
                        else:
                            pnl = (price - row['trade_price']) * row['ending_pos']
                        holding_df.loc[index, ['pnl']] = round(pnl, 3)
                        holding_df.loc[index, ['ending_mv']] = (row['trade_price'] * row['ending_pos']) + pnl
                    except:
                        pass
                        # return 'Price is missing for ' + row['instrument_name'] + ' on ' + str(calc_date)

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
                        0
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
                    0,
                ]

                if calc_date == portfolio_data.inception_date or len(previous_holding) == 0:
                    previous_assets_leverage = 0.0
                    previous_assets_value = 0.0
                else:
                    previous_assets_leverage = previous_holding[previous_holding['type'] == 'Leverage']['ending_mv'].sum()
                    previous_assets_value = previous_holding[previous_holding.type != 'Leverage']['ending_mv'].sum()
                previous_total = previous_assets_value - previous_assets_leverage
                holding_df = holding_df[holding_df.ending_pos != 0]

                # SAVING DATA TO DB

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

                if previous_total != 0.0:
                    period_return = (total - previous_total - total_cash_transactions) / previous_total
                else:
                    period_return = 0.0

                try:
                    nav = Nav.objects.get(date=calc_date, portfolio_code=portfolio_code)
                    nav.cash_val = total_cash
                    nav.pos_val = asset_val
                    nav.short_liab = short_liab
                    nav.total = total
                    nav.period_return = round(period_return, 5)
                    nav.save()
                except:
                    Nav(date=calc_date,
                        portfolio_code=portfolio_code,
                        pos_val=asset_val,
                        cash_val=total_cash,
                        short_liab=short_liab,
                        total=total,
                        period_return=round(period_return, 5)).save()

                if len(error_list) == 0:
                    response_list.append({'portfolio_code': portfolio_code,
                                          'date': calc_date,
                                          'process': 'Valuation',
                                          'exception': '-',
                                          'status': 'Completed',
                                          'comment': 'NAV ' + str(round(total, 2)) + ' ' + str(portfolio_data.currency)})

        calc_date = calc_date + timedelta(days=1)

    return response_list + error_list
