from portfolio.models import Holding, Nav, PortGroup, Portfolio, Transaction, Cash
from instrument.models import Instruments, Prices
from django.db import connection
import pandas as pd
import numpy as np
from datetime import datetime, timezone, timedelta

class AssetValuation:
    def __init__(self, context):
        self.context = context
        self.instrument_code_list = []
        self.prices_table = pd.DataFrame({})
        self.instrument_data_table = pd.DataFrame({})

        # Cash and Margin technical instruments
        cash_instruments = pd.DataFrame(
            Instruments.objects.filter(currency=self.context.base_currency, group='Cash').values())
        self.base_currency_sec_id = int(cash_instruments[cash_instruments['type'] == 'Cash']['id'].values[0])
        self.base_margin_instrument = cash_instruments[cash_instruments['type'] == 'Margin']['id'].values[0]

        # Finance Variables
        self.previous_cash = 0
        self.previous_margin = 0
        self.previous_contra = 0
        self.total_rgl = 0
        self.total_ugl = 0
        self.total_margin = 0
        self.rgl_data = pd.DataFrame({})

        # Valuated Cash and Assets tables
        self.available_cash_df = None
        self.asset_valuation_table = None

        # Transactions tables
        self.previous_transactions = pd.DataFrame({})
        self.current_transactions = pd.DataFrame({})

    def run(self):
        print("ASSET VALUATION", "Current date:", self.context.calc_date, "PREVIOUS date:", self.context.previous_date)

        # FETCHING
        self.fetch_previous_valuation()
        self.fetch_current_transactions()
        self.fetch_instrument_data()
        self.fetch_prices()
        self.fetch_rgl()
        self.fetch_fx_rates()

        # VALUATIONS
        self.asset_valuation()
        self.cash_valuation()
        self.create_final_valuation_table()

        # SAVING
        self.save_valuation(valuation_list=self.context.final_holding_table.to_dict('records'))

    def fetch_instrument_data(self):
        all_transactions = pd.concat([self.previous_transactions, self.current_transactions], ignore_index=True)

        self.instrument_code_list = all_transactions['instrument_id'].drop_duplicates().tolist()
        self.instrument_data_table = pd.DataFrame(Instruments.objects.filter(id__in=self.instrument_code_list).values())

    def fetch_current_transactions(self):
        transactions = Transaction.objects.select_related('security').filter(trade_date=self.context.calc_date,
                                                                             portfolio=self.context.portfolio_data).exclude(security_id__type='Cash')
        transactions_list = [
            {
                'portfolio_code': self.context.portfolio_code, # This part has to be amended or removed later
                'date': self.context.calc_date,
                'trd_id': transaction.id,
                'inv_num': transaction.transaction_link_code,
                'trade_date': self.context.calc_date,
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
        self.current_transactions = pd.DataFrame(transactions_list)

    def fetch_previous_valuation(self):
        previous_valuation = pd.DataFrame(Holding.objects.filter(date=self.context.previous_date,
                                                                 portfolio=self.context.portfolio_data.id).values())

        if not previous_valuation.empty:
            previous_positions = previous_valuation[(previous_valuation['trade_type'] != 'Margin') | previous_valuation['trade_type'] != 'Available Cash']

            self.previous_cash = previous_valuation[previous_valuation['trade_type'] == 'Available Cash']['mv'].sum()
            self.previous_margin = previous_valuation[previous_valuation['trade_type'] == 'Margin']['mv'].sum()
            self.previous_contra = previous_valuation[previous_valuation['trade_type'] == 'Contra']['mv'].sum()

            self.previous_transactions = previous_positions[~previous_positions['instrument_id'].isin([self.base_currency_sec_id, self.base_margin_instrument])]

            return True
        else:
            return False

    def fetch_fx_rates(self):

        """
        Az FX Rateket berakja a kontextusba
        """

        fx_data = Prices.objects.select_related('instrument').filter(date=self.context.calc_date).filter(instrument__type='FX')

        base_df = pd.DataFrame({
            'rate': [self.context.base_currency + '/' + self.context.base_currency],
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
        self.context.fx_rates = pd.concat([fx_df, reverse_fx_df, base_df], ignore_index=True)

    def fetch_rgl(self):
        self.rgl_data = pd.DataFrame(Cash.objects.select_related('transaction').filter(date=self.context.calc_date,
                                                                                       transaction__portfolio=self.context.portfolio_data,
                                                                                       type='Trade PnL').values())

    def fetch_prices(self):
        """
        Lekérdezi az árakat és megjelöli azokat, amelyek
        a mai napon 30 percnél régebbiek.
        """

        prices_df = pd.DataFrame(
            Prices.objects
            .select_related('instrument')
            .filter(date=self.context.calc_date, instrument_id__in=self.instrument_code_list)
            .values()
        )


        if not prices_df.empty:
            prices_df = prices_df.drop(columns=['id', 'date'])

            # Jelenlegi idő UTC-ben
            now = datetime.now(timezone.utc)

            # Új oszlop: created_at_outdated_today
            prices_df['needs_fetching'] = prices_df['created_at'].apply(
                lambda x: x.date() == now.date() and (now - x).total_seconds() > 1800
            )

            self.prices_table = prices_df

        else:
            self.prices_table = pd.DataFrame({
                'instrument_id': [],
                'price': [],
                'source': [],
                'needs_fetching': []
            })

    # --- CALCULATION METHODS ---
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
            self.context.error_list.append({'portfolio_code': self.context.portfolio_data.portfolio_name,
                                    'date': self.context.calc_date,
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
                self.context.error_list.append({'portfolio_code': self.context.portfolio_data.portfolio_name,
                                        'date': self.context.calc_date,
                                        'process': 'Valuation',
                                        'exception': 'Missing Price',
                                        'status': 'Error',
                                        'comment': row['name'] + str(' (') + str(row['instrument_id']) + str(')')
                                        })
            return row['price']

    def prepare_assets_table(self):

        return

    def asset_valuation(self):
        """This part is responsible for the valuation of the assets."""

        # --------------- PREPARE SECTION ------------------------------------------------------------------------------
        # Aggregates CURRENT + PREVIOUS Transactions
        prev_plus_current = pd.concat([self.previous_transactions, self.current_transactions], ignore_index=True)
        prev_plus_current['rgl'] = 0.0

        # Ha a van jelenlegi tranzakció és rgl adat akkor adja hozzá a táblához. Itt jön be az RGL a táblába
        if not self.current_transactions.empty and not self.rgl_data.empty:
            rgl_merge = pd.merge(prev_plus_current, self.rgl_data[['transaction_id', 'base_mv']], left_on='trd_id', right_on='transaction_id', how='left')
            prev_plus_current['rgl'] = rgl_merge['base_mv'].fillna(prev_plus_current['rgl'])

        # --------------- CALCULATION ----------------------------------------------------------------------------------
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

            aggregated_transactions['date'] = self.context.calc_date


            # Kiegészítése a átblának az instrumentum adatokkal
            aggregated_transactions = pd.merge(aggregated_transactions, self.instrument_data_table, left_on='instrument_id', right_on='id', how='left')

            aggregated_transactions['fx_pair'] = aggregated_transactions['currency'] + '/' + self.context.base_currency
            aggregated_transactions = pd.merge(aggregated_transactions, self.context.fx_rates, left_on='fx_pair',
                                               right_on='rate', how='left')
            aggregated_transactions = pd.merge(aggregated_transactions, self.prices_table, left_on='instrument_id',
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
            aggregated_transactions['market_price'] = aggregated_transactions.apply(self.price_cash_security, axis=1)

            # Ide jön a missing pricok lekéréséne a brókertől


            aggregated_transactions['mv'] = round(aggregated_transactions['quantity'] * aggregated_transactions['price'] * aggregated_transactions['fx_rate'], 2)
            aggregated_transactions['margin_req'] = aggregated_transactions['mv'] * aggregated_transactions['margin_rate']

            aggregated_transactions['trd_pnl'] = aggregated_transactions['rgl'] # Ez duplikált oszlop az RGL el
            aggregated_transactions['bv'] = aggregated_transactions.apply(self.book_value_calc, axis=1)
            aggregated_transactions['ugl'] = aggregated_transactions.apply(self.ugl_calc, axis=1)
            aggregated_transactions['price_pnl'] = aggregated_transactions.apply(self.price_pnl_calc, axis=1)
            aggregated_transactions['total_pnl'] = aggregated_transactions['trd_pnl'] + aggregated_transactions['ugl']

            aggregated_transactions = aggregated_transactions.drop(columns=['id', 'name', 'group', 'type', 'currency', 'country', 'fx_pair', 'rate', 'price', 'source'])

            self.total_margin = abs(aggregated_transactions['margin_req'].sum())
            self.total_ugl = aggregated_transactions['ugl'].sum()

            total_bv = aggregated_transactions['bv'].sum()

            total_margin_df = pd.DataFrame({
                'portfolio_code': [self.context.portfolio_code], # this part has to be amaneded or removed later
                'date': [self.context.calc_date],
                'trd_id': [None],
                'inv_num': [0],
                'trade_date': [self.context.calc_date],
                'trade_type': ['Margin'],
                'instrument_id': [self.base_margin_instrument],
                'beg_quantity': [self.previous_margin],
                'quantity': [self.total_margin],
                'trade_price': [1],
                'beg_market_price': [1],
                'market_price': [1],
                'fx_rate': [1],
                'mv': [self.total_margin],
                'beg_bv': [self.previous_margin],
                'bv': [self.total_margin],
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
            if self.total_margin > 0:
                contra_df = pd.DataFrame({
                    'portfolio_code': [self.context.portfolio_code],  # this part has to be amaneded or removed later
                    'date': [self.context.calc_date],
                    'trd_id': [None],
                    'inv_num': [0],
                    'trade_date': [self.context.calc_date],
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

            self.total_rgl = aggregated_transactions['rgl'].sum()

            aggregated_transactions = pd.concat(aggregation_list, ignore_index=True)
            aggregated_transactions = aggregated_transactions[
                ~((aggregated_transactions['quantity'] == 0) & (aggregated_transactions['rgl'] == 0))]
        else:
            # Üres asset táblát ad vissza és az adott periódusra 0 cash értékeket
            aggregated_transactions = pd.DataFrame({})
            self.total_margin = 0
            self.total_ugl = 0
            self.total_rgl = 0

        self.asset_valuation_table = aggregated_transactions

    def cash_valuation(self):
        """
        A cash valuation során, a kontextusba helyezi az egyes capital cash flow elemeket amit más folyamatok használnak.

        Mire ide ér a folyamat már az el ő ző  cash flowt kifetchelte a rendszer. Mivel az az előző valuationből jön.
        """
        capital_cashflow = pd.DataFrame(Transaction.objects.filter(trade_date=self.context.calc_date,
                                                                   portfolio=self.context.portfolio_data,
                                                                   transaction_type__in=['Subscription', 'Redemption',
                                                                                         'Commission',
                                                                                         'Financing']).values())

        if capital_cashflow.empty:
            self.context.subscriptions = 0
            self.context.redemptions = 0
            capital_cash = 0
        else:
            self.context.subscriptions = capital_cashflow[capital_cashflow['transaction_type'] == 'Subscription'][
                'mv'].sum()
            self.context.redemptions = capital_cashflow[capital_cashflow['transaction_type'] == 'Redemption'][
                'mv'].sum()
            capital_cash = capital_cashflow['mv'].sum()

        margin_change = self.previous_margin - self.total_margin  # Cash from margin activity
        total_cash = self.previous_cash + capital_cash + self.total_ugl + margin_change + self.total_rgl

        self.available_cash_df = pd.DataFrame(
            {
                'portfolio_code': [self.context.portfolio_code],  # this part has to be amaneded or removed later
                'date': [self.context.calc_date],
                'trd_id': [None],
                'inv_num': [0],
                'trade_date': [self.context.calc_date],
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

    def create_final_valuation_table(self):
        """
        Ez a metódus össze vonja a cash és az asset értékelést egy közös táblába és további számításokat végez
        """
        self.context.final_holding_table = pd.concat([self.available_cash_df, self.asset_valuation_table], ignore_index=True)
        self.context.final_holding_table = self.context.final_holding_table.replace({np.nan: None})
        self.context.final_holding_table['pos_lev'] = self.context.final_holding_table['mv'] / self.context.final_holding_table['bv'].sum()
        self.context.final_holding_table['weight'] = self.context.final_holding_table['mv'] / self.context.final_holding_table['mv'].sum()
        self.context.final_holding_table['gross_weight'] = self.context.final_holding_table['mv'] / self.context.final_holding_table['mv'].abs().sum()
        self.context.final_holding_table['abs_weight'] = self.context.final_holding_table['mv'].abs() / self.context.final_holding_table[
            'mv'].abs().sum()

    def save_valuation(self, valuation_list):
        # Delete existing holdings
        Holding.objects.filter(
            date=self.context.calc_date,
            portfolio_id=self.context.portfolio_data.id,
        ).delete()

        new_holdings = []

        for valuation in valuation_list:
            # Create a new holding
            new_holdings.append(
                Holding(
                    portfolio_code=valuation['portfolio_code'],
                    portfolio_id=self.context.portfolio_data.id,
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

class NavCalculation:
    def __init__(self, context):
        self.context = context

        self.total_cash_flow = 0.0


    def run(self):
        self.nav_calculation()

    def nav_calculation(self):

        if self.context.portfolio_data.portfolio_type == 'Portfolio Group' or self.context.portfolio_data.portfolio_type == 'Business':
            child_portfolio_ids = PortGroup.objects.filter(parent_id=self.context.portfolio_data.id).values_list(
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
                cursor.execute(query, [self.context.portfolio_data.portfolio_code])  # Prevents SQL injection
                results = cursor.fetchall()

            # Convert results to a list of dictionaries
            data = [
                row[3] for row in results
            ]

            child_portfolios = Portfolio.objects.filter(portfolio_code__in=child_portfolio_ids).values_list('portfolio_code',
                                                                                             flat=True)

            portfolio_navs = pd.DataFrame(
                Nav.objects.filter(date=self.context.calc_date, portfolio_code__in=data).values())

            expected_portfolios = set(child_portfolios)

            # Check if portfolio_navs has data
            if portfolio_navs.empty:
                for port_code in expected_portfolios:
                    self.context.error_list.append({'portfolio_code': self.context.portfolio_data.portfolio_code,
                                            'date': self.context.calc_date,
                                            'process': 'Group Valuation',
                                            'exception': 'Missing Fund Valuation',
                                            'status': 'Error',
                                            'comment': str(port_code) + ' missing fund valuation on ' + str(self.context.calc_date),
                                            })
                return self.context.error_list
            else:
                # Convert the 'portfolio_code' column from portfolio_navs to a set
                available_portfolios = set(portfolio_navs['portfolio_code'])

                # Find missing portfolios
                missing_portfolios = expected_portfolios - available_portfolios

                if missing_portfolios:
                    for port_code in missing_portfolios:
                        self.context.error_list.append({'portfolio_code': self.context.portfolio_data.portfolio_name,
                                                'date': self.context.calc_date,
                                                'process': 'Group Valuation',
                                                'exception': 'Missing Fund Valuation',
                                                'status': 'Error',
                                                'comment': str(port_code) + ' missing fund valuation on ' + str(
                                                    self.context.calc_date),
                                                })
                    return self.context.error_list

            total_cash = portfolio_navs['cash_val'].sum()
            current_nav = portfolio_navs['holding_nav'].sum()
            total_margin = portfolio_navs['margin'].sum()
            total_asset_val = portfolio_navs['pos_val'].sum()

            # P&L numbers
            total_realized_pnl = portfolio_navs['pnl'].sum()
            total_unrealized_pnl = portfolio_navs['unrealized_pnl'].sum()
            total_pnl = portfolio_navs['total_pnl'].sum()

            # Cash Flows
            total_cashflow = portfolio_navs['total_cf'].sum()
        else:
            # NAV numbers
            total_cash = round(self.context.final_holding_table[self.context.final_holding_table['trade_type'] == 'Available Cash']['mv'].sum(), 5)
            current_nav = round(self.context.final_holding_table['bv'].sum(), 5)
            total_margin = round(self.context.final_holding_table[self.context.final_holding_table['trade_type'] == 'Margin']['mv'].sum(), 5)
            total_asset_val = round(self.context.final_holding_table[(self.context.final_holding_table['trade_type'] == 'Sale') | (self.context.final_holding_table['trade_type'] == 'Purchase')]['bv'].sum(), 5)

            # P&L numbers
            total_realized_pnl = round(self.context.final_holding_table['rgl'].sum(), 5)
            total_unrealized_pnl = round(self.context.final_holding_table['ugl'].sum(), 5)
            total_pnl = total_realized_pnl + total_unrealized_pnl

            # Cash Flows
            total_cashflow = self.context.subscriptions + self.context.redemptions

        # print('REAL', total_realized_pnl, 'UNREAL', total_unrealized_pnl, total_unrealized_pnl + total_realized_pnl , self.calc_date)
        self.context.total_nav = current_nav

        try:
            nav = Nav.objects.get(date=self.context.calc_date, portfolio_id=self.context.portfolio_data)
            nav.portfolio_id = self.context.portfolio_data.id
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
            nav.subscription = self.context.subscriptions
            nav.redemption = self.context.redemptions
            nav.total_cf = total_cashflow
            nav.save()
        except:

            Nav(date=self.context.calc_date,
                portfolio_code=self.context.portfolio_code, # this part has to be amaneded or removed later
                portfolio_id=self.context.portfolio_data.id,
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
                subscription=self.context.subscriptions,
                redemption=self.context.redemptions,
                total_cf=total_cashflow,
                price_return=0,
                trade_return=0).save()

        if len(self.context.error_list) == 0:
            self.context.response_list.append({'portfolio_code': self.context.portfolio_data.portfolio_name,
                                       'date': self.context.calc_date,
                                       'process': 'NAV Valuation',
                                       'exception': '-',
                                       'status': 'Completed',
                                       'comment': 'NAV ' + str(round(current_nav, 2)) + ' ' + str(self.context.portfolio_data.currency)})
        else:
            self.context.error_list.append({'portfolio_code': self.context.portfolio_data.portfolio_name,
                                       'date': self.context.calc_date,
                                       'process': 'NAV Valuation',
                                       'exception': 'Incorrect Valuation',
                                       'status': 'Alert',
                                       'comment': 'NAV ' + str(round(current_nav, 2)) + ' ' + str(
                                           self.context.portfolio_data.currency)})