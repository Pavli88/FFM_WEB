from portfolio.models import Transaction, Holding, Nav, Portfolio, Cash, UGL, PortGroup
from instrument.models import Instruments, Prices
import pandas as pd
import numpy as np
from datetime import datetime, date
from datetime import timedelta

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
        self.previous_cash = 0
        self.previous_margin = 0
        self.previous_ugl = 0
        self.previous_transactions = pd.DataFrame({})
        self.final_df = pd.DataFrame({})

    def fetch_transactions(self):
        transactions = Transaction.objects.select_related('security').filter(trade_date=self.calc_date,
                                                                             portfolio=self.portfolio_data).exclude(security_id__type='Cash')
        transactions_list = [
            {
                'portfolio_code': self.portfolio_code, # This part has to be amended or removed later
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

    def fetch_previous_valuation(self, previous_date, portfolio_id):
        previous_valuations = pd.DataFrame(Holding.objects.filter(date=previous_date,
                                                                  portfolio=portfolio_id).values())

        if not previous_valuations.empty:
            previous_positions = previous_valuations[
                (previous_valuations['trade_type'] != 'Margin') | previous_valuations['trade_type'] != 'Available Cash']
            self.previous_cash = previous_valuations[previous_valuations['trade_type'] == 'Available Cash']['mv'].sum()
            self.previous_margin = previous_valuations[previous_valuations['trade_type'] == 'Margin']['mv'].sum()


            self.previous_transactions = previous_positions[~previous_positions['instrument_id'].isin([self.base_currency_sec_id, self.base_margin_instrument])]
            self.previous_ugl = self.previous_transactions['ugl'].sum()

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
        return pd.DataFrame(Cash.objects.select_related('transaction').filter(date=self.calc_date,
                                                                              transaction__portfolio=self.portfolio_data,
                                                                              type='Trade PnL').values())
        # return pd.DataFrame(Cash.objects.filter(date=self.calc_date,
        #                                         portfolio_code=self.portfolio_code, type='Trade PnL').values())

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
        try:
            existing_trade = self.previous_transactions[self.previous_transactions['trd_id'] == row['trd_id']]
            return row['bv'] - existing_trade['bv'].sum()
        except:
            return row['bv']


    def book_value_calc(self, row):
        if row['group'] == 'CFD':
            if row['quantity'] > 0:
                return round((row['price'] - row['trade_price']) * row['quantity'] * row['fx_rate'], 2)
            else:
                return round((row['trade_price'] - row['price']) * abs(row['quantity']) * row['fx_rate'], 2)
        else:
            return row['mv']

    def fx_check(self, row):
        if row['fx_rate'] == 0:
            self.error_list.append({'portfolio_code': self.portfolio_data.portfolio_name,
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
                self.error_list.append({'portfolio_code': self.portfolio_data.portfolio_name,
                                     'date': self.calc_date,
                                     'process': 'Valuation',
                                     'exception': 'Missing Price',
                                     'status': 'Error',
                                     'comment': row['name'] + str(' (') + str(row['instrument_id']) + str(')')
                                        })
            return row['price']

    def asset_valuation(self):
        # print('PREVOUS DATE', self.previous_date, 'CURRENT DATE', self.calc_date)

        # FETCHING----------------------------------------------

        # Previous Valuations
        self.fetch_previous_valuation(previous_date=self.previous_date, portfolio_id=self.portfolio_data)

        # Current Transactions
        current_transactions = self.fetch_transactions()

        prev_plus_current = pd.concat([self.previous_transactions, current_transactions], ignore_index=True)
        prev_plus_current['rgl'] = 0.0

        # RGL
        rgl_data = self.fetch_rgl()

        if not current_transactions.empty and not rgl_data.empty:
            rgl_merge = pd.merge(prev_plus_current, rgl_data[['transaction_id', 'base_mv']], left_on='trd_id', right_on='transaction_id', how='left')
            prev_plus_current['rgl'] = rgl_merge['base_mv'].fillna(prev_plus_current['rgl'])

        #  FX
        fx_rates = self.fetch_fx_rates(date=self.calc_date)

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
            aggregated_transactions['bv'] = aggregated_transactions.apply(self.book_value_calc, axis=1)
            aggregated_transactions['ugl'] = aggregated_transactions.apply(self.ugl_calc, axis=1)
            aggregated_transactions['margin_req'] = aggregated_transactions['mv'] * aggregated_transactions['margin_rate']
            aggregated_transactions = aggregated_transactions.drop(columns=['id', 'name', 'group', 'type', 'currency', 'country', 'fx_pair', 'rate', 'price', 'source'])

            total_margin = abs(aggregated_transactions['margin_req'].sum())
            total_ugl = aggregated_transactions['ugl'].sum()
            total_rgl = aggregated_transactions['rgl'].sum()
            total_bv = aggregated_transactions['bv'].sum()

            total_margin_df = pd.DataFrame({
                'portfolio_code': [self.portfolio_code], # this part has to be amaneded or removed later
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

            if total_margin > 0:
                contra_df = pd.DataFrame({
                    'portfolio_code': [self.portfolio_code], # this part has to be amaneded or removed later
                    'date': [self.calc_date],
                    'trd_id': [None],
                    'inv_num': [0],
                    'trade_date': [self.calc_date],
                    'trade_type': ['Contra'],
                    'instrument_id': [self.base_currency_sec_id],
                    'quantity': [total_bv* -1],
                    'trade_price': [1],
                    'market_price': [1],
                    'fx_rate': [1],
                    'mv': [total_bv * -1],
                    'bv': [total_bv * -1],
                    'weight': [0.0],
                    'ugl': [0.0],
                    'rgl': [0.0],
                    'margin_rate': [0.0],
                    'margin_req': [0.0]
                })
                aggregation_list = [aggregated_transactions, total_margin_df, contra_df]
            else:
                aggregation_list = [aggregated_transactions, total_margin_df]

            # print(margin_cash_list)
            aggregated_transactions = pd.concat(aggregation_list, ignore_index=True)
            aggregated_transactions = aggregated_transactions[
                ~((aggregated_transactions['quantity'] == 0) & (aggregated_transactions['rgl'] == 0))]
        else:
            aggregated_transactions = pd.DataFrame({})
            total_margin = 0
            total_ugl = 0
            total_rgl = 0
        # It will iterate through the final positions based on the sec group type

        # CASH VALUATION ----------------------------------
        capital_cash = self.capital_cash_calculation()
        margin_change = self.previous_margin - total_margin
        # # ugl_change = total_ugl
        total_cash = self.previous_cash + total_rgl + capital_cash + total_ugl + margin_change

        available_cash_df = pd.DataFrame(
            {
                'portfolio_code': [self.portfolio_code], # this part has to be amaneded or removed later
                'date': [self.calc_date],
                'trd_id': [None],
                'inv_num': [0],
                'trade_date': [self.calc_date],
                'trade_type': ['Available Cash'],
                'instrument_id': [self.base_currency_sec_id],
                'quantity': [total_cash],
                'trade_price': [1],
                'market_price': [1],
                'fx_rate': [1],
                'mv': [total_cash],
                'bv': [total_cash],
                'weight': [0.0],
                'ugl': [0.0],
                'rgl': [0.0],
                'margin_rate': [0.0],
                'margin_req': [0.0]
            }
        )

        self.final_df = pd.concat([available_cash_df, aggregated_transactions], ignore_index=True)
        self.final_df = self.final_df.replace({np.nan: None})
        self.final_df['weight'] = self.final_df['mv']/ self.final_df['mv'].sum()
        self.final_df['pos_lev'] = self.final_df['mv'] / self.final_df['bv'].sum()
        self.save_valuation(valuation_list=self.final_df.to_dict('records'))

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

    def capital_cash_calculation(self):
        capital_cashflow = pd.DataFrame(Transaction.objects.filter(trade_date=self.calc_date,
                                                                   portfolio=self.portfolio_data,
                                                                   transaction_type__in=['Subscription', 'Redemption',
                                                                                         'Commission', 'Financing']).values())

        if capital_cashflow.empty:
            self.subscriptions = 0
            self.redemptions = 0
            return 0
        else:
            self.subscriptions = capital_cashflow[capital_cashflow['transaction_type'] == 'Subscription']['mv'].sum()
            self.redemptions = capital_cashflow[capital_cashflow['transaction_type'] == 'Redemption']['mv'].sum()
            return capital_cashflow['mv'].sum()

    def nav_calculation(self, calc_date):

        if self.portfolio_data.portfolio_type == 'Portfolio Group' or self.portfolio_data.portfolio_type == 'Business':
            child_portfolio_ids = PortGroup.objects.filter(parent_id=self.portfolio_data.id).values_list(
                'portfolio_id', flat=True)

            child_portfolios = Portfolio.objects.filter(id__in=child_portfolio_ids).values_list('portfolio_code',
                                                                                                flat=True)
            portfolio_navs = pd.DataFrame(
                Nav.objects.filter(date=calc_date, portfolio_code__in=child_portfolios).values())

            expected_portfolios = set(child_portfolios)

            # Check if portfolio_navs has data
            if portfolio_navs.empty:
                for port_code in expected_portfolios:
                    self.error_list.append({'portfolio_code': self.portfolio_data.portfolio_code,
                                            'date': calc_date,
                                            'process': 'Group Valuation',
                                            'exception': 'Missing Fund Valuation',
                                            'status': 'Error',
                                            'comment': str(port_code) + ' missing fund valuation on ' + str(calc_date),
                                            })
                return self.error_list
            else:
                # Convert the 'portfolio_code' column from portfolio_navs to a set
                available_portfolios = set(portfolio_navs['portfolio_code'])

                # Find missing portfolios
                missing_portfolios = expected_portfolios - available_portfolios

                if missing_portfolios:
                    for port_code in missing_portfolios:
                        self.error_list.append({'portfolio_code': self.portfolio_data.portfolio_name,
                                                'date': calc_date,
                                                'process': 'Group Valuation',
                                                'exception': 'Missing Fund Valuation',
                                                'status': 'Error',
                                                'comment': str(port_code) + ' missing fund valuation on ' + str(
                                                    calc_date),
                                                })
                    return self.error_list

            total_cash = portfolio_navs['cash_val'].sum()
            current_nav = portfolio_navs['holding_nav'].sum()
            total_margin = portfolio_navs['margin'].sum()
            total_asset_val = portfolio_navs['pos_val'].sum()

            # P&L numbers
            total_realized_pnl = portfolio_navs['pnl'].sum()
            total_unrealized_pnl = portfolio_navs['unrealized_pnl'].sum()
            total_pnl = portfolio_navs['total_pnl'].sum()

            # Cash Flows
            subscriptions = portfolio_navs['subscription'].sum()
            redemptions = portfolio_navs['redemption'].sum()
            total_cashflow = portfolio_navs['total_cf'].sum()
        else:
            # NAV numbers
            total_cash = round(self.final_df[self.final_df['trade_type'] == 'Available Cash']['mv'].sum(), 5)
            current_nav = round(self.final_df['bv'].sum(), 5)
            total_margin = round(self.final_df[self.final_df['trade_type'] == 'Margin']['mv'].sum(), 5)
            total_asset_val = round(self.final_df[(self.final_df['trade_type'] == 'Sale') | (self.final_df['trade_type'] == 'Purchase')]['bv'].sum(), 5)

            # P&L numbers
            total_realized_pnl = round(self.final_df['rgl'].sum(), 5)
            total_unrealized_pnl = round(self.final_df['ugl'].sum(), 5)
            total_pnl = total_realized_pnl + total_unrealized_pnl

            # Cash Flows
            subscriptions = self.subscriptions
            redemptions = self.redemptions
            total_cashflow = self.subscriptions + self.redemptions
        # print('REAL', total_realized_pnl, 'UNREAL', total_unrealized_pnl, total_unrealized_pnl + total_realized_pnl , self.calc_date)

        try:
            nav = Nav.objects.get(date=calc_date, portfolio_id=self.portfolio_data)
            nav.portfolio_id = self.portfolio_data.id
            nav.cash_val = total_cash
            nav.margin = total_margin
            nav.pos_val = total_asset_val
            nav.short_liab = 0
            nav.holding_nav = current_nav
            nav.pnl = total_realized_pnl
            nav.unrealized_pnl = total_unrealized_pnl
            nav.total_pnl = total_pnl
            nav.ugl_diff = 0
            nav.trade_return = 0
            nav.price_return = 0
            nav.cost = 0
            nav.subscription = subscriptions
            nav.redemption = redemptions
            nav.total_cf = total_cashflow
            nav.save()
        except:
            Nav(date=calc_date,
                portfolio_code=self.portfolio_code, # this part has to be amaneded or removed later
                portfolio_id=self.portfolio_data.id,
                pos_val=total_asset_val,
                cash_val=total_cash,
                margin=total_margin,
                short_liab=0,
                holding_nav=current_nav,
                pnl=total_realized_pnl,
                unrealized_pnl=total_unrealized_pnl,
                total_pnl = total_pnl,
                ugl_diff=0,
                cost=0,
                subscription=subscriptions,
                redemption=redemptions,
                total_cf=total_cashflow,
                price_return=0,
                trade_return=0).save()

        if len(self.error_list) == 0:
            self.response_list.append({'portfolio_code': self.portfolio_data.portfolio_name,
                                       'date': calc_date,
                                       'process': 'NAV Valuation',
                                       'exception': '-',
                                       'status': 'Completed',
                                       'comment': 'NAV ' + str(round(current_nav, 2)) + ' ' + str(self.portfolio_data.currency)})
        else:
            self.response_list.append({'portfolio_code': self.portfolio_data.portfolio_name,
                                       'date': calc_date,
                                       'process': 'NAV Valuation',
                                       'exception': 'Incorrect Valuation',
                                       'status': 'Alert',
                                       'comment': 'NAV ' + str(round(current_nav, 2)) + ' ' + str(
                                           self.portfolio_data.currency)})

    def save_valuation(self, valuation_list):
        # Delete existing holdings
        Holding.objects.filter(
            date=self.calc_date,
            portfolio=self.portfolio_data,
        ).delete()

        new_holdings = []

        for valuation in valuation_list:
            # Create a new holding
            new_holdings.append(
                Holding(
                    portfolio_code=valuation['portfolio_code'],
                    portfolio=self.portfolio_data,
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
                    pos_lev=valuation['pos_lev'],
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

    if calc_date < valuation.portfolio_data.inception_date and valuation.portfolio_data.portfolio_type != 'Portfolio Group':
        valuation.add_error_message({'portfolio_code': portfolio_code,
                                     'date': calc_date,
                                     'process': 'Valuation',
                                     'exception': 'Incorrect Valuation Start Date',
                                     'status': 'Error',
                                     'comment': 'Valuation start date is less then portfolio inception date: ' + str(valuation.portfolio_data.inception_date)})
        return valuation.send_responses()

    # Checking if fund is funded
    if valuation.portfolio_data.status == 'Not Funded' and valuation.portfolio_data.portfolio_type != 'Portfolio Group' and valuation.portfolio_data.portfolio_type != 'Business':
        valuation.add_error_message({'portfolio_code': portfolio_code,
                                     'date': calc_date,
                                     'process': 'Valuation',
                                     'exception': 'Not Funded',
                                     'status': 'Error',
                                     'comment': 'Portfolio is not funded. Valuation is not possible'})
        return valuation.send_responses()

    while calc_date <= date.today():
        if valuation.portfolio_data.weekend_valuation is False and (
                calc_date.weekday() == 6 or calc_date.weekday() == 5):
            print('---', calc_date, calc_date.strftime('%A'), 'Not calculate')
        else:
            if valuation.portfolio_data.weekend_valuation is False and calc_date.weekday() == 0:
                time_back = 3
            else:
                time_back = 1
            previous_date = calc_date - timedelta(days=time_back)

            if valuation.portfolio_data.portfolio_type == 'Portfolio Group' or valuation.portfolio_data.portfolio_type == 'Business':
                valuation.nav_calculation(calc_date=calc_date)
            else:
                valuation.calc_date = calc_date
                valuation.previous_date = previous_date
                valuation.asset_valuation()
                valuation.nav_calculation(calc_date=calc_date)
        calc_date = calc_date + timedelta(days=1)
    return valuation.send_responses()
