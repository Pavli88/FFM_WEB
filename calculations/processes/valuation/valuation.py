from weakref import finalize

from portfolio.models import Transaction, TransactionPnl, Holding, Nav, Portfolio, Cash, RGL, UGL, Margin
from instrument.models import Instruments, Prices, Tickers
import pandas as pd
import numpy as np
from datetime import datetime, date
from django.db import connection
from datetime import timedelta
from django.db.models import Q
from sqlparse.engine.grouping import group


class Valuation():
    def __init__(self, portfolio_code, calc_date):
        self.portfolio_code = portfolio_code
        self.calc_date = calc_date
        self.previous_date = None
        self.fx_rates = None
        self.transactions = None
        self.previous_valuation = None
        self.total_cash_flow = 0.0
        self.subscriptions = 0.0
        self.redemptions = 0.0
        self.response_list = []
        self.error_list = []
        self.portfolio_data = Portfolio.objects.get(portfolio_code=portfolio_code)
        self.base_currency = self.portfolio_data.currency
        self.holding_df = []
        self.instrument_code_list = []
        cash_instruments = pd.DataFrame(Instruments.objects.filter(currency=self.base_currency, group='Cash').values())
        self.base_currency_sec_id = int(cash_instruments[cash_instruments['type'] == 'Cash']['id'].values[0])
        self.base_margin_instrument = cash_instruments[cash_instruments['type'] == 'Margin']['id'].values[0]
        self.previous_capital = pd.DataFrame({})
        self.previous_margin = pd.DataFrame({})
        self.previous_transactions = pd.DataFrame({})
        self.final_df = pd.DataFrame({})

    def fetch_transactions(self):
        transactions = Transaction.objects.select_related('security').filter(trade_date=self.calc_date,
                                                                             portfolio_code=self.portfolio_code).exclude(security_id__type='Cash')
        transactions_list = [
            {
                'portfolio_code': self.portfolio_code,
                'date': self.calc_date,
                'trd_id': transaction.id,
                'inv_num': transaction.transaction_link_code,
                'trade_date': self.calc_date,
                'trade_type': transaction.transaction_type,
                'instrument_id': transaction.security_id,
                'quantity': transaction.quantity,  # -> Needed for valuation
                'trade_price': transaction.price,
                'market_price': 0.0,  # -> Needed for valuation
                'fx_rate': 0.0,  # -> Needed for valuation
                'mv': 0.0,
                'bv': 0.0,
                'weight': 0.0,
                'ugl': 0.0,
                'rgl': 0.0,
                'margin_rate': transaction.margin_rate
            }
            for transaction in transactions
        ]
        return pd.DataFrame(transactions_list)

    def fetch_instrument_data(self, instrument_code_list):
        return pd.DataFrame(Instruments.objects.filter(id__in=instrument_code_list).values())

    def fetch_previous_valuation(self, previous_date, portfolio_code):
        previous_valuations = pd.DataFrame(Holding.objects.filter(date=previous_date,
                                                                  portfolio_code=portfolio_code).exclude(trade_type__in=['Cash Margin', 'Margin']).values())
        if not previous_valuations.empty:
            self.previous_capital = previous_valuations[previous_valuations['trade_type'] == 'Capital']
            self.previous_capital['trd_id'] = None
            self.previous_transactions = previous_valuations[~previous_valuations['instrument_id'].isin([self.base_currency_sec_id, self.base_margin_instrument])]

    def fetch_fx_rates(self, date):
        fx_data = Prices.objects.select_related('instrument').filter(date=date).filter(instrument__type='FX')
        base_df = pd.DataFrame({
            'rate': [self.base_currency + '/' + self.base_currency],
            'fx_rate': [1]
        })
        reverse_fx_df = pd.DataFrame({
            'rate': [],
            'fx_rate': []
        })
        if fx_data.exists():
            fx_pairs_list = []
            for fx_pair in fx_data:
                fx_pairs_list.append({
                    'rate': fx_pair.instrument.name,
                    'fx_rate': fx_pair.price,
                })
            fx_df = pd.DataFrame(fx_pairs_list)
            reverse_fx_df['rate'] = fx_df['rate'].apply(lambda x: '/'.join(x.split('/')[::-1]))
            reverse_fx_df['fx_rate'] = 1 / fx_df['fx_rate']
        else:
            fx_df = pd.DataFrame({
                'rate': [],
                'fx_rate': []
            })
        self.fx_rates = pd.concat([fx_df, reverse_fx_df, base_df], ignore_index=True)
        return self.fx_rates

    def fetch_rgl(self):
        return pd.DataFrame(Cash.objects.filter(date=self.calc_date,
                                                portfolio_code=self.portfolio_code, type='Trade PnL').values())

    def fetch_prices(self, date, instrument_code_list):
        prices_df = pd.DataFrame(Prices.objects.select_related('instrument').filter(date=date).filter(instrument_id__in=instrument_code_list).values())
        if not prices_df.empty:
            return prices_df.drop(columns=['id', 'date'])
        else:
            return pd.DataFrame({
                'instrument_id': [],
                'price': [],
                'source': []
            })

    def ugl_calc(self, row):
        if row['quantity'] > 0:
            return round((row['price'] - row['trade_price']) * row['quantity'] * row['fx_rate'], 2)
        else:
            return round((row['trade_price'] - row['price']) * abs(row['quantity']) * row['fx_rate'], 2)

    def book_value_calc(self, row):
        if row['group'] == 'CFD':
            return row['ugl']
        else:
            return row['mv']

    def fx_check(self, row):
        if row['fx_rate'] == 0:
            self.error_list.append({'portfolio_code': self.portfolio_code,
                                    'date': self.calc_date,
                                    'process': 'Valuation',
                                    'exception': 'Missing FX Rate',
                                    'status': 'Error',
                                    'comment': row['fx_pair']})

    def price_cash_security(self, row):
        self.fx_check(row)

        if row['group'] == 'Cash':
            return 1
        else:
            if row['price'] == 0:
                self.error_list.append({'portfolio_code': self.portfolio_code,
                                     'date': self.calc_date,
                                     'process': 'Valuation',
                                     'exception': 'Missing Price',
                                     'status': 'Error',
                                     'comment': row['name'] + str(' (') + str(row['instrument_id']) + str(')')
                                        })
            return row['price']

    def asset_valuation(self):
        print('')
        print('ASSET VALUATION-------------------------------------------')
        print('PREVOUS DATE', self.previous_date, 'CURRENT DATE', self.calc_date)

        # FETCHING----------------------------------------------

        # Previous Valuations
        self.fetch_previous_valuation(previous_date=self.previous_date, portfolio_code=self.portfolio_code)

        # print('')
        # print('PREVOUS TRANSACTIONS')
        # print(self.previous_transactions)

        # Current Transactions
        current_transactions = self.fetch_transactions()
        # print('')
        # print('CURERNT TRANSACTIONS')
        # print(current_transactions)
        #

        prev_plus_current = pd.concat([self.previous_transactions, current_transactions], ignore_index=True)
        prev_plus_current['rgl'] = 0.0
        # print('')
        # print('PREV + CURRENT TRAN')
        # print(prev_plus_current)
        # print('-------------------------------------------------------------')

        # RGL
        rgl_data = self.fetch_rgl()
        # print('')
        # print('RGL DATA')
        # print(rgl_data)

        if not current_transactions.empty and not rgl_data.empty:
            rgl_merge = pd.merge(prev_plus_current, rgl_data[['transaction_id', 'base_mv']], left_on='trd_id', right_on='transaction_id', how='left')
            prev_plus_current['rgl'] = rgl_merge['base_mv'].fillna(prev_plus_current['rgl'])

        #  FX
        fx_rates = self.fetch_fx_rates(date=self.calc_date)
        # print(fx_rates)

        if not prev_plus_current.empty:
            aggregated_transactions = prev_plus_current.groupby('inv_num', as_index=False).agg({
                'quantity': 'sum',
                'portfolio_code': 'first',
                'date': 'first',
                'trd_id': 'first',
                'inv_num': 'first',
                'trade_date': 'first',
                'trade_type': 'first',
                'instrument_id': 'first',
                'trade_price': 'first',
                'mv': 'first',
                'bv': 'first',
                'weight': 'first',
                'ugl': 'first',
                'rgl': 'sum',
                'margin_rate': 'first'
            })

            aggregated_transactions['date'] = self.calc_date
            instrument_code_list = aggregated_transactions['instrument_id'].drop_duplicates().tolist()
            instrument_df = self.fetch_instrument_data(instrument_code_list)

            prices_df = self.fetch_prices(date=self.calc_date, instrument_code_list=instrument_code_list)

            aggregated_transactions = pd.merge(aggregated_transactions, instrument_df, left_on='instrument_id', right_on='id', how='left')
            aggregated_transactions['fx_pair'] = aggregated_transactions['currency'] + '/' + self.base_currency
            aggregated_transactions = pd.merge(aggregated_transactions, fx_rates, left_on='fx_pair',
                                               right_on='rate', how='left')
            aggregated_transactions = pd.merge(aggregated_transactions, prices_df, left_on='instrument_id',
                                               right_on='instrument_id', how='left')
            aggregated_transactions['price'].fillna(0, inplace=True)
            aggregated_transactions['fx_rate'].fillna(0, inplace=True)
            aggregated_transactions['market_price'] = aggregated_transactions.apply(self.price_cash_security, axis=1)
            aggregated_transactions['mv'] = round(aggregated_transactions['quantity'] * aggregated_transactions['price'] * aggregated_transactions['fx_rate'], 2)
            aggregated_transactions['ugl'] = aggregated_transactions.apply(self.ugl_calc, axis=1)
            aggregated_transactions['bv'] = aggregated_transactions.apply(self.book_value_calc, axis=1)
            aggregated_transactions['margin_req'] = aggregated_transactions['mv'] * aggregated_transactions['margin_rate']
            aggregated_transactions = aggregated_transactions.drop(columns=['id', 'name', 'group', 'type', 'currency', 'country', 'fx_pair', 'rate', 'price', 'source'])

            total_margin = abs(aggregated_transactions['margin_req'].sum())
            total_margin_df = pd.DataFrame({
                'portfolio_code': [self.portfolio_code],
                'date': [self.calc_date],
                'trd_id': [None],
                'inv_num': [0],
                'trade_date': [self.calc_date],
                'trade_type': ['Margin'],
                'instrument_id': [self.base_margin_instrument],
                'quantity': [total_margin],
                'trade_price': [1],
                'market_price': [1],
                'fx_rate': [1],
                'mv': [total_margin],
                'bv': [total_margin],
                'weight': [0.0],
                'ugl': [0.0],
                'rgl': [0.0],
                'margin_rate': [0.0],
                'margin_req': [0.0]
            })
            total_margin_cash_df = pd.DataFrame(
                {
                    'portfolio_code': [self.portfolio_code],
                    'date': [self.calc_date],
                    'trd_id': [None],
                    'inv_num': [0],
                    'trade_date': [self.calc_date],
                    'trade_type': ['Cash Margin'],
                    'instrument_id': [self.base_currency_sec_id],
                    'quantity': [total_margin * -1],
                    'trade_price': [1],
                    'market_price': [1],
                    'fx_rate': [1],
                    'mv': [total_margin * -1],
                    'bv': [total_margin * -1],
                    'weight': [0.0],
                    'ugl': [0.0],
                    'rgl': [0.0],
                    'margin_rate': [0.0],
                    'margin_req': [0.0]
                }
            )

            # print(margin_cash_list)
            aggregated_transactions = pd.concat([aggregated_transactions, total_margin_cash_df, total_margin_df], ignore_index=True)
            aggregated_transactions = aggregated_transactions[
                ~((aggregated_transactions['quantity'] == 0) & (aggregated_transactions['rgl'] == 0))]
            # print('')
            # print('AGGREGATED TRANSACTIONS')
            # print(aggregated_transactions)
            # print('')
        else:
            aggregated_transactions = pd.DataFrame({})

        # It will iterate through the final positions based on the sec group type

        # CASH VALUATION ----------------------------------
        # This is needed at the end because of the CFD position valuation. On CFD the BV is the UGL.
        cash_transactions = self.cash_calculation()


        self.final_df = pd.concat([cash_transactions, aggregated_transactions], ignore_index=True)
        self.final_df = self.final_df.replace({np.nan: None})
        self.save_valuation(valuation_list=self.final_df.to_dict('records'))
        self.nav_calculation(calc_date=self.calc_date, previous_date=self.previous_date, portfolio_code=self.portfolio_code)

    def save_ugl(self, valuation_list):

        # Gather Holding objects to update existing records
        existing_ugls = UGL.objects.filter(
            date=self.calc_date,
            portfolio_code=self.portfolio_code,
            transaction_id__in=[valuation['trd_id'] for valuation in valuation_list],
            )
        existing_ugls_dict = {
            (ugl.transaction_id): ugl for ugl in existing_ugls
        }

        new_ugls = []
        updated_ugls = []

        for valuation in valuation_list:
            trd_num = valuation['trd_id']

            if trd_num in existing_ugls_dict:
                # Update existing holding
                holding = existing_ugls_dict[trd_num]
                holding.base_mv = valuation['ugl']
            else:
                # Create a new holding
                new_ugls.append(
                    UGL(
                        portfolio_code=valuation['portfolio_code'],
                        date=valuation['date'],
                        transaction_id=trd_num,
                        base_mv=valuation['ugl'],
                    )
                )

        # Perform bulk updates and insertions
        if updated_ugls:
            UGL.objects.bulk_update(updated_ugls, [
                'inv_num',
                'trade_date',
                'instrument_id',
                'quantity',
                'trade_price',
                'market_price',
            ])

        if new_ugls:
            UGL.objects.bulk_create(new_ugls)

    def cash_calculation(self):
        cash_data = Cash.objects.select_related('transaction').filter(date=self.calc_date, portfolio_code=self.portfolio_code)
        capital_df = pd.DataFrame(cash_data.values())

        if not capital_df.empty:
            self.subscriptions = capital_df[capital_df['type'] == 'Subscription']['base_mv'].sum()
            self.redemptions = capital_df[capital_df['type'] == 'Redemption']['base_mv'].sum()

        cash_list = [
            {
                'portfolio_code': self.portfolio_code,
                'date': self.calc_date,
                'trd_id': None,
                'inv_num': 0,
                'trade_date': self.calc_date,
                'trade_type': 'Capital',
                'instrument_id': self.base_currency_sec_id,
                'quantity': cash.base_mv,
                'trade_price': cash.transaction.fx_rate,
                'market_price': 1,
                'fx_rate': 1,
                'mv': cash.base_mv,
                'bv': cash.base_mv,
                'weight': 0.0,
                'ugl': 0.0,
                'rgl': 0.0,
                'margin_rate': 0.0,
                'margin_req': 0
            }
            for cash in cash_data
        ]
        cash_df = pd.DataFrame(cash_list)
        cash_df = pd.concat([cash_df, self.previous_capital], ignore_index=True)
        cash_df['date'] = self.calc_date
        cash_df = cash_df.groupby('instrument_id', as_index=False).agg({
                'quantity': 'sum',
                'portfolio_code': 'first',
                'date': 'first',
                'trd_id': 'first',
                'inv_num': 'first',
                'trade_date': 'first',
                'trade_type': 'first',
                'instrument_id': 'first',
                'trade_price': 'first',
                'mv': 'sum',
                'bv': 'sum',
                'weight': 'first',
                'ugl': 'first',
                'rgl': 'sum',
                'margin_rate': 'first',
                'market_price': 'first',
                'fx_rate': 'first'
            })
        return cash_df

    def nav_calculation(self, calc_date, previous_date, portfolio_code):
        # # Previous NAV
        # previous_nav = Nav.objects.filter(portfolio_code=portfolio_code, date=previous_date).values()

        total_cash = self.final_df[(self.final_df['trade_type'] == 'Cash Margin') | (self.final_df['trade_type'] == 'Capital')]['mv'].sum()
        current_nav = self.final_df['bv'].sum()

        # if len(previous_nav) == 0:
        #     previous_nav = 0
        #     previous_holding_nav = 0
        #     prev_ugl = 0
        # else:
        #     previous_holding_nav = previous_nav[0]['holding_nav']
        #     prev_ugl = previous_nav[0]['unrealized_pnl']
        #     previous_nav = previous_nav[0]['total']
        #
        # # Total NAV
        total_realized_pnl = round(self.final_df['rgl'].sum(), 2)
        total_unrealized_pnl = round(self.final_df['ugl'].sum(), 2)
        # total = previous_nav + self.total_external_flow + total_realized_pnl
        # ugl_diff = total_unrealized_pnl - prev_ugl
        #
        # # Total Return Calculation
        # if previous_nav != 0.0:
        #     period_return = total_realized_pnl / previous_nav
        # else:
        #     period_return = 0.0
        #
        # total_asset_value = self.final_df[self.final_df['']]
        #
        # if self.portfolio_data.calc_holding == True:
        #     asset_value = total_asset_value.sum() # -> Update
        #     cash_value = self.total_cash_flow
        #     liability =
        #     h_nav = self.final_df['bv'].sum()
        # else:
        #     asset_value = 0.0
        #     cash_value = 0.0
        #     liability = 0.0
        #     h_nav = 0.0

        # if self.portfolio_data.calc_holding == True and previous_holding_nav != 0.0:
        #     dietz_return = round(ugl_diff / previous_holding_nav, 4)
        # else:
        #     dietz_return = 0.0

        try:
            nav = Nav.objects.get(date=calc_date, portfolio_code=portfolio_code)
            nav.cash_val = total_cash
            nav.pos_val = 0
            nav.short_liab = 0
            nav.total = self.final_df['bv'].sum() - total_unrealized_pnl
            nav.holding_nav = current_nav
            nav.pnl = total_realized_pnl
            nav.unrealized_pnl = total_unrealized_pnl
            nav.total_pnl = total_realized_pnl + total_realized_pnl
            nav.ugl_diff = 0
            nav.trade_return = 0
            nav.price_return = 0
            nav.cost = 0
            nav.subscription = self.subscriptions
            nav.redemption = self.redemptions
            nav.total_cf = self.subscriptions + self.redemptions
            nav.save()
        except:
            Nav(date=calc_date,
                portfolio_code=portfolio_code,
                pos_val=0,
                cash_val=total_cash,
                short_liab=0,
                total=self.final_df['bv'].sum() - total_unrealized_pnl,
                holding_nav=current_nav,
                pnl=total_realized_pnl,
                unrealized_pnl=total_unrealized_pnl,
                total_pnl = total_realized_pnl + total_realized_pnl,
                ugl_diff=0,
                cost=0,
                subscription=self.subscriptions,
                redemption=self.redemptions,
                total_cf=self.subscriptions + self.redemptions,
                price_return=0,
                trade_return=0).save()

        if len(self.error_list) == 0:
            self.response_list.append({'portfolio_code': portfolio_code,
                                       'date': calc_date,
                                       'process': 'NAV Valuation',
                                       'exception': '-',
                                       'status': 'Completed',
                                       'comment': 'NAV ' + str(round(current_nav, 2)) + ' ' + str(self.portfolio_data.currency)})
        else:
            self.response_list.append({'portfolio_code': portfolio_code,
                                       'date': calc_date,
                                       'process': 'NAV Valuation',
                                       'exception': 'Incorrect Valuation',
                                       'status': 'Alert',
                                       'comment': 'NAV ' + str(round(current_nav, 2)) + ' ' + str(
                                           self.portfolio_data.currency)})

    def save_valuation(self, valuation_list):
        print('SAVING VALUATION')

        # Delete existing holdings
        Holding.objects.filter(
            date=self.calc_date,
            portfolio_code=self.portfolio_code,
        ).delete()

        new_holdings = []

        for valuation in valuation_list:
            # Create a new holding
            new_holdings.append(
                Holding(
                    portfolio_code=valuation['portfolio_code'],
                    date=valuation['date'],
                    trd_id=valuation['trd_id'],
                    inv_num=valuation['inv_num'],
                    trade_date=str(valuation['trade_date']),
                    trade_type=valuation['trade_type'],
                    instrument_id=valuation['instrument_id'],
                    quantity=round(valuation['quantity'], 4),
                    trade_price=valuation['trade_price'],
                    market_price=valuation['market_price'],
                    fx_rate=valuation['fx_rate'],
                    mv=round(valuation['mv'], 4),
                    bv=round(valuation['bv'], 4),
                    weight=valuation['weight'],
                    rgl=valuation['rgl'],
                    ugl=valuation['ugl'],
                    margin_rate=valuation['margin_rate'],
                )
            )
        if new_holdings:
            Holding.objects.bulk_create(new_holdings)

    def add_error_message(self, message):
        self.error_list.append(message)

    def send_responses(self):
        return self.response_list + self.error_list


def calculate_holdings(portfolio_code, calc_date):
    pd.set_option('display.width', 200)
    calc_date = datetime.strptime(str(calc_date), '%Y-%m-%d').date()

    valuation = Valuation(portfolio_code=portfolio_code, calc_date=calc_date)

    if calc_date < valuation.portfolio_data.inception_date:
        valuation.add_error_message({'portfolio_code': portfolio_code,
                                     'date': calc_date,
                                     'process': 'Valuation',
                                     'exception': 'Incorrect Valuation Start Date',
                                     'status': 'Error',
                                     'comment': 'Valuation start date is less then portfolio inception date: ' + str(valuation.portfolio_data.inception_date)})
        return valuation.send_responses()

    # Checking if fund is funded
    if valuation.portfolio_data.status == 'Not Funded':
        valuation.add_error_message({'portfolio_code': portfolio_code,
                                     'date': calc_date,
                                     'process': 'Valuation',
                                     'exception': 'Not Funded',
                                     'status': 'Error',
                                     'comment': 'Portfolio is not funded. Valuation is not possible'})
        return valuation.send_responses()

    while calc_date <= date.today():
        if valuation.portfolio_data.weekend_valuation is False and (calc_date.weekday() == 6 or calc_date.weekday() == 5):
            print('---', calc_date, calc_date.strftime('%A'), 'Not calculate')
        else:
            if valuation.portfolio_data.weekend_valuation is False and calc_date.weekday() == 0:
                time_back = 3
            else:
                time_back = 1

            previous_date = calc_date - timedelta(days=time_back)

            # valuation.fetch_previous_valuation(previous_date=previous_date, portfolio_code=portfolio_code)
            # if calc_date != valuation.portfolio_data.inception_date: #valuation.previous_valuation.empty
            #     valuation.add_error_message({'portfolio_code': portfolio_code,
            #                                  'date': calc_date,
            #                                  'process': 'Valuation',
            #                                  'exception': 'Missing Valuation',
            #                                  'status': 'Error',
            #                                  'comment': 'Missing valuation on ' + str(previous_date)})
            #     valuation.add_error_message({'portfolio_code': portfolio_code,
            #                                  'date': calc_date,
            #                                  'process': 'Valuation',
            #                                  'exception': 'Stopped Valuation',
            #                                  'status': 'Error',
            #                                  'comment': 'Valuation stopped due to missing previous valuation'})
            #     break
            valuation.calc_date = calc_date
            valuation.previous_date = previous_date
            valuation.asset_valuation()
            # valuation.cash_calculation()
            # valuation.save_holding(trade_date=calc_date,
            #                        portfolio_code=portfolio_code,
            #                        holding_data=valuation.holding_df)
            # valuation.nav_calculation(calc_date=calc_date,
            #                           previous_date=previous_date,
            #                           portfolio_code=portfolio_code)
        calc_date = calc_date + timedelta(days=1)
    return valuation.send_responses()
