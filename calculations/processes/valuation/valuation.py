from portfolio.models import Transaction, Holding, Nav, Portfolio, Cash, UGL, PortGroup
from instrument.models import Instruments, Prices
from calculations.models import ProcessAudit, ProcessException
import pandas as pd
import numpy as np
from datetime import datetime, date
from datetime import timedelta
from django.db import connection
from django.utils.timezone import now
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from calculations.processes.loggers.ProcessAuditLogger import ProcessAuditLogger

# Beépiteni, hogy ha a valuadion date a jelenlegi dátum akkor nézze meg hogy a legutolsó ár 30 percnél nem öregebb,
# a igen a user kérje le a brókerétől éd updatelje a price táblát így más tudja használni aki 30 percen belül akar ujra valuationt

# Két esetbe kell lekérni a brókertől az árat:
# 1. Valuation today és 30 percnél öregebb a legutolsó ár
# 2. Valuation not today but price is missing for that day

class Valuation():
    def __init__(self, portfolio_code, request_date):
        self.portfolio_code = portfolio_code
        self.request_date = request_date
        self.calc_date = None
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
        self.user_id = self.portfolio_data.user_id
        self.base_currency = self.portfolio_data.currency
        self.holding_df = []
        self.instrument_code_list = []
        cash_instruments = pd.DataFrame(Instruments.objects.filter(currency=self.base_currency, group='Cash').values())
        self.base_currency_sec_id = int(cash_instruments[cash_instruments['type'] == 'Cash']['id'].values[0])
        self.base_margin_instrument = cash_instruments[cash_instruments['type'] == 'Margin']['id'].values[0]
        self.previous_cash = 0
        self.previous_margin = 0
        self.previous_contra = 0
        self.previous_ugl = 0
        self.previous_transactions = pd.DataFrame({})
        self.final_df = pd.DataFrame({})
        self.missing_prices_instrument_id_list = []
        self.total_nav = 0.0
        self.skip_processing = False
        self.error_message = ""
        self.start_date_type = None

        # Calling portfolio validation during Valuation initialization
        self.validate_portfolio()

        # Start date beállítása ha a validálás sikeres
        if self.skip_processing == False:
            self.set_start_date()

    # VALIDATIONS
    def validate_portfolio(self):
        """
        Ellenőrzi az indulási dátumot és a funding státuszt.
        Beállítja a self.skip_processing és self.error_message attribútumokat.
        """
        self.skip_processing = False
        self.error_message = ""

        if self.portfolio_data.status == 'Not Funded' and self.portfolio_data.portfolio_type not in ['Portfolio Group',
                                                                                                     'Business']:
            self.add_error_message({
                'portfolio_code': self.portfolio_code,
                'date': self.request_date,
                'process': 'Valuation',
                'exception': 'Not Funded',
                'status': 'Error',
                'comment': 'Portfolio is not funded. Valuation is not possible'
            })
            self.skip_processing = True
            self.error_message = 'Portfolio is not funded'

    def set_start_date(self):
        if self.request_date < self.portfolio_data.inception_date and self.portfolio_data.portfolio_type != 'Portfolio Group':
            self.calc_date = self.portfolio_data.inception_date
            self.start_date_type = 'Inception'
            return

        latest_nav = Nav.objects.filter(portfolio_code=self.portfolio_code).order_by('-date').first()

        if latest_nav and latest_nav.date < self.request_date:
            self.calc_date = latest_nav.date
            self.start_date_type = 'Latest NAV Date'
        elif not latest_nav:
            self.calc_date = self.portfolio_data.inception_date
            self.start_date_type = 'No NAV, Inception'
        else:
            self.calc_date = self.request_date
            self.start_date_type = 'Request Date'

    # --- FETCHING SECTIONS ---
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

    def fetch_previous_valuation(self):
        self.previous_valuation = pd.DataFrame(Holding.objects.filter(date=self.previous_date,
                                                                      portfolio=self.portfolio_data.id).values())

        if not self.previous_valuation.empty:
            previous_positions = self.previous_valuation[
                (self.previous_valuation['trade_type'] != 'Margin') | self.previous_valuation['trade_type'] != 'Available Cash']
            self.previous_cash = self.previous_valuation[self.previous_valuation['trade_type'] == 'Available Cash']['mv'].sum()
            self.previous_margin = self.previous_valuation[self.previous_valuation['trade_type'] == 'Margin']['mv'].sum()
            self.previous_contra = self.previous_valuation[self.previous_valuation['trade_type'] == 'Contra']['mv'].sum()

            self.previous_transactions = previous_positions[~previous_positions['instrument_id'].isin([self.base_currency_sec_id, self.base_margin_instrument])]
            self.previous_ugl = self.previous_transactions['ugl'].sum()
            return True
        else:
            return False

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

    # --- CALCULATION SECTIONS ---
    # Asset valuation related function
    def ugl_calc(self, row):
        try:
            existing_trade = self.previous_transactions[self.previous_transactions['trd_id'] == row['trd_id']]
            # if existing_trade['beg_quantity'] > 0 and existing_trade['quantity'] == 0:
            #     return 0
            return row['bv'] - existing_trade['bv'].sum()
        except:
            return row['bv']

    def trade_pnl_calc(self, row):
        try:
            print(row)
            existing_trade = self.previous_transactions[self.previous_transactions['trd_id'] == row['trd_id']]

            value = row['mv'] + existing_trade['mv'].sum()
            return value
        except:
            return 0

    def previous_value(self, row, value):
        try:
            existing_trade = self.previous_transactions[self.previous_transactions['trd_id'] == row['trd_id']]
            return existing_trade[value].iloc[0]
        except:
            return 0

    def price_pnl_calc(self, row):
        if row['mv'] == 0:
            return 0
        else:
            return row['ugl']

    def price_ret_calc(self, row):
        if row['mv'] == 0:
            return 0
        else:
            if row['group'] == 'Cash':
                return 0

            if self.calc_date == row['trade_date']:
                # leverage = row['leverage']
                return row['price_pnl'] / (row['quantity'] * row['trade_price'])
            else:
                prev_bv = row['bv'] - row['ugl']
                return row['price_pnl'] / prev_bv

    def book_value_calc(self, row):
        # Here comes the logic for other assett types

        # # If this is a fully closed trasaction it is 0
        if row['quantity'] == 0:
            return 0

        if row['group'] == 'CFD':
            if row['quantity'] > 0:
                # Purchase trade book value calculation
                return round((row['price'] - row['trade_price']) * row['quantity'] * row['fx_rate'], 2)
            elif row['quantity'] < 0:
                # Sale trade book value caluclation
                return round((row['trade_price'] - row['price']) * abs(row['quantity']) * row['fx_rate'], 2)
        else:
            # If this is not leveraged trade the book value is equal to the market value
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
                self.missing_prices_instrument_id_list.append(row['instrument_id'])
                self.error_list.append({'portfolio_code': self.portfolio_data.portfolio_name,
                                     'date': self.calc_date,
                                     'process': 'Valuation',
                                     'exception': 'Missing Price',
                                     'status': 'Error',
                                     'comment': row['name'] + str(' (') + str(row['instrument_id']) + str(')')
                                        })
            return row['price']

    # --- PROCESS SECTION ---
    def asset_valuation(self):
        """This part is responsible for the valuation of the assets."""

        # FETCHING----------------------------------------------
        # # Previous Valuations
        # self.fetch_previous_valuation()

        # Current Transactions
        current_transactions = self.fetch_transactions()

        # Összevonja az előző valuation és az adott periódus tranzakcióit és az rgl t 0 ra állitja
        prev_plus_current = pd.concat([self.previous_transactions, current_transactions], ignore_index=True)
        prev_plus_current['rgl'] = 0.0

        # RGL
        rgl_data = self.fetch_rgl()

        # Ha a van jelenlegi tranzakció és rgl adat akkor adja hozzá a táblához. Itt jön be az RGL a táblába
        if not current_transactions.empty and not rgl_data.empty:
            rgl_merge = pd.merge(prev_plus_current, rgl_data[['transaction_id', 'base_mv']], left_on='trd_id', right_on='transaction_id', how='left')
            prev_plus_current['rgl'] = rgl_merge['base_mv'].fillna(prev_plus_current['rgl'])

        #  FX
        fx_rates = self.fetch_fx_rates(date=self.calc_date)

        # Ha nem üres az eőző periódus és a jelenlegi tranzakciók akkor kezdi az értékelést
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

            # Previous Values
            aggregated_transactions['beg_quantity'] = aggregated_transactions.apply(
                lambda row: self.previous_value(row, 'quantity'), axis=1)
            aggregated_transactions['beg_market_price'] = aggregated_transactions.apply(
                lambda row: self.previous_value(row, 'market_price'), axis=1)
            aggregated_transactions['beg_mv'] = aggregated_transactions.apply(
                lambda row: self.previous_value(row, 'mv'), axis=1)
            aggregated_transactions['beg_bv'] = aggregated_transactions.apply(
                lambda row: self.previous_value(row, 'bv'), axis=1)

            aggregated_transactions['price'].fillna(0, inplace=True)
            aggregated_transactions['fx_rate'].fillna(0, inplace=True)

            # Számolás
            # Cash papirok áraqzása 1-re
            # print(self.missing_prices_instrument_id_list)
            aggregated_transactions['market_price'] = aggregated_transactions.apply(self.price_cash_security, axis=1)

            # Ide jön a missing pricok lekéréséne a brókertől




            # print(set(self.missing_prices_instrument_id_list))
            aggregated_transactions['mv'] = round(aggregated_transactions['quantity'] * aggregated_transactions['price'] * aggregated_transactions['fx_rate'], 2)
            aggregated_transactions['margin_req'] = aggregated_transactions['mv'] * aggregated_transactions[
                'margin_rate']

            aggregated_transactions['trd_pnl'] = aggregated_transactions['rgl'] # Ez duplikált oszlop az RGL el
            aggregated_transactions['bv'] = aggregated_transactions.apply(self.book_value_calc, axis=1)
            aggregated_transactions['ugl'] = aggregated_transactions.apply(self.ugl_calc, axis=1)

            aggregated_transactions['price_pnl'] = aggregated_transactions.apply(self.price_pnl_calc, axis=1)

            aggregated_transactions['total_pnl'] = aggregated_transactions['trd_pnl'] + aggregated_transactions[
                'ugl']

            aggregated_transactions = aggregated_transactions.drop(columns=['id', 'name', 'group', 'type', 'currency', 'country', 'fx_pair', 'rate', 'price', 'source'])

            total_margin = abs(aggregated_transactions['margin_req'].sum())
            total_ugl = aggregated_transactions['ugl'].sum()
            total_bv = aggregated_transactions['bv'].sum()

            total_margin_df = pd.DataFrame({
                'portfolio_code': [self.portfolio_code], # this part has to be amaneded or removed later
                'date': [self.calc_date],
                'trd_id': [None],
                'inv_num': [0],
                'trade_date': [self.calc_date],
                'trade_type': ['Margin'],
                'instrument_id': [self.base_margin_instrument],
                'beg_quantity': [self.previous_margin],
                'quantity': [total_margin],
                'trade_price': [1],
                'beg_market_price': [1],
                'market_price': [1],
                'fx_rate': [1],
                'mv': [total_margin],
                'beg_bv': [self.previous_margin],
                'bv': [total_margin],
                'pos_lev': [0.0],
                'weight': [0.0],
                'gross_weight': [0.0],
                'abs_weight': [0.0],
                'ugl': [0.0],
                'rgl': [0.0],
                'margin_rate': [0.0],
                'margin_req': [0.0],
                'price_pnl': [0.0],
                'trd_pnl': [0.0],
                'total_pnl': [0.0],
            })
            # Mivel lezáródik az ügylet így nincs kontra ezért a realizált teljes értéke cashbe megy
            if total_margin > 0:
                contra_df = pd.DataFrame({
                    'portfolio_code': [self.portfolio_code],  # this part has to be amaneded or removed later
                    'date': [self.calc_date],
                    'trd_id': [None],
                    'inv_num': [0],
                    'trade_date': [self.calc_date],
                    'trade_type': ['Contra'],
                    'instrument_id': [self.base_currency_sec_id],
                    'beg_quantity': [self.previous_contra],
                    'quantity': [total_bv * -1],
                    'trade_price': [1],
                    'beg_market_price': [1],
                    'market_price': [1],
                    'fx_rate': [1],
                    'mv': [total_bv * -1],
                    'beg_bv': [self.previous_contra],
                    'bv': [total_bv * -1],
                    'pos_lev': [0.0],
                    'weight': [0.0],
                    'gross_weight': [0.0],
                    'abs_weight': [0.0],
                    'ugl': [0.0],
                    'rgl': [0.0],
                    'margin_rate': [0.0],
                    'margin_req': [0.0],
                    'price_pnl': [0.0],
                    'trd_pnl': [0.0],
                    'total_pnl': [0.0],
                })
                aggregation_list = [aggregated_transactions, total_margin_df, contra_df]
                # total_rgl = 0
            else:
                aggregation_list = [aggregated_transactions, total_margin_df]

            total_rgl = aggregated_transactions['rgl'].sum()

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
        total_cash = self.previous_cash + capital_cash + total_ugl + margin_change + total_rgl

        available_cash_df = pd.DataFrame(
            {
                'portfolio_code': [self.portfolio_code], # this part has to be amaneded or removed later
                'date': [self.calc_date],
                'trd_id': [None],
                'inv_num': [0],
                'trade_date': [self.calc_date],
                'trade_type': ['Available Cash'],
                'instrument_id': [self.base_currency_sec_id],
                'beg_quantity': [self.previous_cash],
                'quantity': [total_cash],
                'trade_price': [1],
                'beg_market_price': [0.0],
                'market_price': [1],
                'fx_rate': [1],
                'mv': [total_cash],
                'beg_bv': [self.previous_cash],
                'bv': [total_cash],
                'pos_lev': [0.0],
                'weight': [0.0],
                'gross_weight': [0.0],
                'abs_weight': [0.0],
                'ugl': [0.0],
                'rgl': [0.0],
                'margin_rate': [0.0],
                'margin_req': [0.0],
                'price_pnl': [0.0],
                'trd_pnl': [0.0],
                'total_pnl': [0.0],
            }
        )

        self.final_df = pd.concat([available_cash_df, aggregated_transactions], ignore_index=True)
        self.final_df = self.final_df.replace({np.nan: None})
        self.final_df['pos_lev'] = self.final_df['mv'] / self.final_df['bv'].sum()
        self.final_df['weight'] = self.final_df['mv']/ self.final_df['mv'].sum()
        self.final_df['gross_weight'] = self.final_df['mv'] / self.final_df['mv'].abs().sum()
        self.final_df['abs_weight'] = self.final_df['mv'].abs() / self.final_df['mv'].abs().sum()

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

            query = """
                    WITH RECURSIVE portfolio_hierarchy AS (
                        -- Base case: Select the given Portfolio Group using its portfolio_code
                        SELECT p.id             AS parent_id, \
                               p.portfolio_name AS parent_name, \
                               p.portfolio_type, \
                               p.portfolio_code, \
                               p.id             AS child_id, \
                               p.portfolio_name AS child_name, \
                               p.portfolio_type AS child_type, \
                               p.portfolio_code AS child_code
                        FROM portfolio_portfolio p
                        WHERE p.portfolio_code = %s -- Parameterized query

                        UNION ALL

                        -- Recursive case: Find all children of the current parent in the hierarchy
                        SELECT ph.child_id       AS parent_id, \
                               ph.child_name     AS parent_name, \
                               ph.child_type     AS portfolio_type, \
                               ph.child_code     AS portfolio_code, \
                               p2.id             AS child_id, \
                               p2.portfolio_name AS child_name, \
                               p2.portfolio_type AS child_type, \
                               p2.portfolio_code AS child_code
                        FROM portfolio_hierarchy ph
                                 JOIN portfolio_portgroup pr ON ph.child_id = pr.parent_id
                                 JOIN portfolio_portfolio p2 ON pr.portfolio_id = p2.id)
                    -- Retrieve only Automated portfolios from the hierarchy
                    SELECT child_id, child_name, child_type, child_code
                    FROM portfolio_hierarchy
                    WHERE child_type = 'Portfolio';
                    """

            # Execute query
            with connection.cursor() as cursor:
                cursor.execute(query, [self.portfolio_data.portfolio_code])  # Prevents SQL injection
                results = cursor.fetchall()

            # Convert results to a list of dictionaries
            data = [
                row[3] for row in results
            ]

            child_portfolios = Portfolio.objects.filter(portfolio_code__in=child_portfolio_ids).values_list('portfolio_code',
                                                                                             flat=True)

            portfolio_navs = pd.DataFrame(
                Nav.objects.filter(date=calc_date, portfolio_code__in=data).values())

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
        self.total_nav = current_nav

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
            self.error_list.append({'portfolio_code': self.portfolio_data.portfolio_name,
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
            portfolio_id=self.portfolio_data.id,
        ).delete()

        new_holdings = []

        for valuation in valuation_list:
            # Create a new holding
            new_holdings.append(
                Holding(
                    portfolio_code=valuation['portfolio_code'],
                    portfolio_id=self.portfolio_data.id,
                    date=valuation['date'],
                    trd_id=valuation['trd_id'],
                    inv_num=valuation['inv_num'],
                    trade_date=str(valuation['trade_date']),
                    trade_type=valuation['trade_type'],
                    instrument_id=valuation['instrument_id'],
                    beg_quantity=valuation['beg_quantity'],
                    quantity=round(valuation['quantity'], 4),
                    trade_price=valuation['trade_price'],
                    beg_market_price=valuation['beg_market_price'],
                    market_price=valuation['market_price'],
                    fx_rate=valuation['fx_rate'],
                    mv=round(valuation['mv'], 4),
                    beg_bv=valuation['beg_bv'],
                    bv=round(valuation['bv'], 4),
                    weight=valuation['weight'],
                    pos_lev=valuation['pos_lev'],
                    rgl=valuation['rgl'],
                    ugl=valuation['ugl'],
                    margin_rate=valuation['margin_rate'],
                    price_pnl=valuation['price_pnl'],
                    trd_pnl=valuation['trd_pnl'],
                    total_pnl=valuation['total_pnl'],
                    gross_weight=valuation['gross_weight'],
                    abs_weight=valuation['abs_weight'],

                )
            )

        if new_holdings:
            Holding.objects.bulk_create(new_holdings)


    # Messaging
    def add_error_message(self, message):
        self.error_list.append(message)

    def send_responses(self):
        df = pd.DataFrame(self.error_list)
        df_unique = df.drop_duplicates()
        self.error_list = df_unique.to_dict('records')
        return self.error_list

def serialize_exceptions(exceptions):
    for e in exceptions:
        if isinstance(e.get("date"), date):
            e["date"] = e["date"].isoformat()
    return exceptions

def calculate_holdings(portfolio_code, calc_date=date.today(), manual_request=False):
    pd.set_option('display.width', 200)

    # CHANNELS LAYER CONNECTION ----------------------------------------------------------------------------------------
    channel_layer = get_channel_layer()
    calc_date = datetime.strptime(str(calc_date), '%Y-%m-%d').date()
    # ------------------------------------------------------------------------------------------------------------------

    print('')
    print('REQUEST START DATE', calc_date)

    valuation = Valuation(portfolio_code=portfolio_code, request_date=calc_date)

    print("CALC RANGE:", valuation.calc_date, date.today(), valuation.start_date_type)
    # end_date = date(2025, 5, 14)
    # date.today()

    if valuation.skip_processing:
        print('Skipped processing')
        process_audit_logger = ProcessAuditLogger(process_name='Valuation', portfolio=valuation.portfolio_data, valuation_date=calc_date)
        process_audit_logger.complete(status='Error', message='Not funded portfolio', exception_list=valuation.send_responses())
    else:
        current_iteration_date = valuation.calc_date
        while current_iteration_date <= date.today():
            print(current_iteration_date)

            # New Process Audit
            process_audit_logger = ProcessAuditLogger(process_name='Valuation',
                                                      portfolio=valuation.portfolio_data,
                                                      valuation_date=current_iteration_date)

            # --- VALUATION FUTTATÁSA ---
            # Check if the current iteration day is weekend and weekend valuation is allowed
            if valuation.portfolio_data.weekend_valuation is False and (
                    current_iteration_date.weekday() == 6 or current_iteration_date.weekday() == 5):
                print('---', current_iteration_date, current_iteration_date.strftime('%A'), 'Not calculate')
            else:
                if valuation.portfolio_data.weekend_valuation is False and current_iteration_date.weekday() == 0:
                    time_back = 3
                else:
                    time_back = 1

                previous_date = current_iteration_date - timedelta(days=time_back)

                if valuation.portfolio_data.portfolio_type == 'Portfolio Group' or valuation.portfolio_data.portfolio_type == 'Business':
                    valuation.nav_calculation(calc_date=current_iteration_date)
                else:
                    valuation.calc_date = current_iteration_date
                    valuation.previous_date = previous_date

                    # Checking if prevous valuation exists
                    valuation.fetch_previous_valuation()
                    valuation.asset_valuation()
                    valuation.nav_calculation(calc_date=current_iteration_date)

            current_iteration_date = current_iteration_date + timedelta(days=1)


            # ----------------------------- End of process audit -----------------------------------------------------

            process_audit_logger.complete(status='Alert' if len(valuation.error_list) > 0 else 'Completed',
                                          message=f"{len(valuation.send_responses())} issues" if valuation.send_responses() else f"NAV: {valuation.total_nav} {valuation.base_currency}",
                                          exception_list=valuation.send_responses())

            #Sending Notification if this is a Dashboard request
            if manual_request == False and len(valuation.send_responses()) > 0:
                async_to_sync(channel_layer.group_send)(
                    f"user_{valuation.user_id}",
                    {
                        "type": "process.notification",
                        "payload": {
                            "process": 'valuation',
                            "message": "Valuation completed with exceptions.",
                            "exceptions": serialize_exceptions(valuation.send_responses())
                        }
                    }
                )



