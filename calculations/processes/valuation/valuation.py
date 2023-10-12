from portfolio.models import Transaction, TransactionPnl, Holding, Nav, Portfolio
from instrument.models import Instruments, Prices
import pandas as pd
import numpy as np
from datetime import datetime, date
from django.db import connection
from datetime import timedelta
from django.db.models import Q


class Valuation():
    def __init__(self, portfolio_code, calc_date):
        self.portfolio_code = portfolio_code
        self.calc_date = calc_date
        self.fx_rates = ''
        self.transactions = ''
        self.previous_valuation = ''
        self.total_cash_flow = 0.0
        self.asset_df = ''
        self.total_external_flow = 0.0
        self.total_leverage = 0.0
        self.response_list = []
        self.error_list = []
        self.portfolio_data = Portfolio.objects.get(portfolio_code=portfolio_code)
        self.portfolio_cash_security = Instruments.objects.get(currency=self.portfolio_data.currency,
                                                               group='Cash')
        self.leverage_security = Instruments.objects.get(currency=self.portfolio_data.currency,
                                                         type='Leverage')

    def initialize_dataframe(self):
        self.holding_df = pd.DataFrame({
            'transaction_id': [],
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
            'fx_rate': [],
            'beginning_mv': [],
            'ending_mv': [],
            'unrealized_pnl': []
        })

    def fetch_transactions(self, trade_date):
        cursor = connection.cursor()
        cursor.execute(
            """
            select
            pt.id, name, security, quantity, price, mv,
   pt.currency, trading_cost, transaction_type, transaction_link_code,
   trade_date, sec_group, type, margin_balance, net_cashflow,
   realized_pnl, financing_cost, local_cashflow, local_mv, local_pnl,
   fx_pnl, fx_rate, country
            from portfolio_transaction as pt, instrument_instruments as inst
where pt.security = inst.id
and pt.portfolio_code = '{portfolio_code}'
and pt.trade_date = '{trade_date}'
            """.format(trade_date=trade_date,
                       portfolio_code=self.portfolio_code)
        )
        current_transactions = cursor.fetchall()
        df = pd.DataFrame(current_transactions, columns=[col[0] for col in cursor.description])

        asset_flows = df[df['sec_group'] != 'Cash']
        asset_flows['base_cashflow'] = asset_flows['net_cashflow']
        asset_flows['base_margin_balance'] = asset_flows['margin_balance']
        for index, trade in asset_flows.iterrows():
            if trade['currency'] == self.portfolio_data.currency:
                asset_flows.at[index, 'base_cashflow'] = trade['net_cashflow']
            else:
                fx_rate = self.fx_rates[self.fx_rates['name'] == trade['name']]['fx_rate'].sum()
                asset_flows.at[index, 'base_cashflow'] = trade['net_cashflow'] * fx_rate
                asset_flows.at[index, 'base_margin_balance'] = trade['margin_balance'] * fx_rate
        self.asset_df = asset_flows
        self.transactions = df

    def fetch_previous_valuation(self, previous_date, portfolio_code):
        try:
            self.previous_valuation = pd.read_json(Holding.objects.get(date=previous_date, portfolio_code=portfolio_code).data)
        except Holding.DoesNotExist:
            self.previous_valuation = pd.DataFrame({})

    def load_fx_rates(self, trade_date):
        cursor = connection.cursor()
        cursor.execute(
            """ 
            select
        name, currency, type, date, price
        from instrument_instruments as inst, instrument_prices as ip
        where
        inst.id = ip.inst_code
        and inst.type = 'FX'
        and inst.name
        like
        '%/%'
        and date = '{trade_date}';
            """.format(trade_date=trade_date))
        currency_rates = pd.DataFrame(cursor.fetchall(), columns=[col[0] for col in cursor.description])
        currency_rates['reverse_price'] = 1 / currency_rates['price']
        currency_rates['base_currency'] = currency_rates.name.str[0:3]
        currency_rates['reverse_pair'] = currency_rates.name.str[4:] + '/' + currency_rates.name.str[0:3]
        currency_rates['fx_rate'] = currency_rates['price']

        for index, rate in currency_rates.iterrows():
            if rate['base_currency'] == self.portfolio_data.currency and rate[
                'currency'] != self.portfolio_data.currency:
                currency_rates.at[index, 'fx_rate'] = rate['reverse_price']
            elif rate['base_currency'] != self.portfolio_data.currency and rate[
                'currency'] == self.portfolio_data.currency:
                pass
            else:
                searched_pair = rate['currency'] + '/' + self.portfolio_data.currency
                filtered_currency_df_1 = currency_rates[currency_rates['name'] == searched_pair]['price']
                filtered_currency_df_2 = currency_rates[currency_rates['reverse_pair'] == searched_pair][
                    'reverse_price']

                try:
                    if len(filtered_currency_df_1) == 0:
                        conversion_price = filtered_currency_df_2.tolist()[0]
                    else:
                        conversion_price = filtered_currency_df_1.tolist()[0]
                    currency_rates.at[index, 'fx_rate'] = conversion_price * rate['price']
                except:
                    currency_rates.at[index, 'fx_rate'] = 0.0
                    self.error_list.append({'portfolio_code': self.portfolio_code,
                                            'date': trade_date,
                                            'process': 'Valuation',
                                            'exception': 'Missing FX Rate',
                                            'status': 'Error',
                                            'comment': 'Missing FX Coversion Rate: ' + rate['name'] + ' - ' + self.portfolio_data.currency + ' to ' + rate['name'][4:]})
        self.fx_rates = currency_rates

    def asset_valuation(self):
        # PROCESSING EXISTING TRANSACTIONS AND NEW RELATED TRANSACTIONS
        try:
            previous_assets = self.previous_valuation[(self.previous_valuation['type'] != 'Cash') & (self.previous_valuation['type'] != 'Leverage')]
        except:
            previous_assets = pd.DataFrame({})
        if previous_assets.empty is not True:
            for index, trade in previous_assets.iterrows():
                # Filtering for linked transactions
                try:
                    linked_transactions = self.asset_df[self.asset_df['transaction_link_code'] == trade['transaction_id']]
                    linked_quantity = linked_transactions['quantity'].sum()
                except:
                    linked_quantity = 0.0

                self.holding_df.loc[len(self.holding_df.index)] = [
                    trade['transaction_id'],
                    trade['instrument_name'],
                    trade['instrument_id'],
                    trade['group'],
                    trade['type'],
                    trade['currency'],
                    str(trade['trade_date']),
                    trade['transaction_type'],
                    trade['ending_pos'],
                    trade['ending_pos'] - abs(linked_quantity),
                    0,
                    round(trade['trade_price'], 4),
                    0,
                    1,
                    trade['ending_mv'],
                    trade['ending_mv'],
                    0]

        # PROCESSING NEW TRASACTIONS AND RELATED TRANSACTIONS
        for index, trade in self.asset_df.iterrows():
            if trade['transaction_link_code'] == 0:

                # Filtering for linked transactions
                linked_transactions = self.asset_df[self.asset_df['transaction_link_code'] == trade['id']]
                self.holding_df.loc[len(self.holding_df.index)] = [
                    trade['id'],
                    trade['name'],
                    trade['security'],
                    trade['sec_group'],
                    trade['type'],
                    trade['currency'],
                    str(trade['trade_date']),
                    trade['transaction_type'],
                    0,
                    trade['quantity'] - abs(linked_transactions['quantity'].sum()),
                    0,
                    round(trade['price'], 4),
                    0,
                    1,
                    0,
                    0,
                    0]

        # POSITION VALUATION
        intrument_list = list(dict.fromkeys(self.holding_df['instrument_id']))
        prices_df = pd.DataFrame(Prices.objects.filter(date=self.calc_date, inst_code__in=intrument_list).values())

        for index, trade in self.holding_df.iterrows():
            if trade['currency'] == self.portfolio_data.currency:
                fx_rate = 1
            else:
                searched_pair = trade['currency'] + '/' + self.portfolio_data.currency
                fx_rate = self.fx_rates[self.fx_rates['name'] == searched_pair]
                if fx_rate.empty:
                    fx_rate = self.fx_rates[self.fx_rates['reverse_pair'] == searched_pair]
                fx_rate = fx_rate['fx_rate'].sum()

            try:
                valuation_price = list(prices_df[prices_df['inst_code'] == trade['instrument_id']]['price'])[0]
            except:
                self.error_list.append(
                    {'portfolio_code': self.portfolio_code,
                     'date': self.calc_date,
                     'process': 'Valuation',
                     'exception': 'Missing Price',
                     'status': 'Error',
                     'comment': 'Missing Price for ID (' + str(trade['instrument_id']) + ')'}
                )
                valuation_price = 1

            self.holding_df.at[index, 'valuation_price'] = valuation_price
            self.holding_df.at[index, 'fx_rate'] = fx_rate

            if trade['ending_pos'] == 0.0:
                unrealized_pnl = 0.0
            else:
                if trade['transaction_type'] == 'Purchase':
                    unrealized_pnl = trade['ending_pos'] * (valuation_price - trade['trade_price']) * fx_rate
                else:
                    unrealized_pnl = trade['ending_pos'] * (trade['trade_price'] - valuation_price) * fx_rate

            self.holding_df.at[index, 'unrealized_pnl'] = unrealized_pnl
            self.holding_df.at[index, 'ending_mv'] = trade['ending_pos'] * valuation_price * fx_rate
        self.holding_df = self.holding_df[(self.holding_df.ending_pos != 0) | (self.holding_df.beginning_pos != 0)]

    def leverage_calculation(self):

        if self.previous_valuation.empty:
            previous_leverage = 0.0
        else:
            previous_leverage = self.previous_valuation[self.previous_valuation['type'] == 'Leverage']['ending_mv'].sum()

        leverage_df = pd.DataFrame({
            'transaction_id': ['-'],
            'instrument_name': ['Leverage'],
            'instrument_id': [0],
            'group': ['Leverage'],
            'type': ['Leverage'],
            'currency': [self.portfolio_data.currency],
            'trade_date': [str(self.calc_date)],
            'transaction_type': ['Leverage'],
            'beginning_pos': [previous_leverage],
            'ending_pos': [previous_leverage + self.asset_df['base_margin_balance'].sum()],
            'change': [previous_leverage + self.asset_df['base_margin_balance'].sum() - previous_leverage],
            'trade_price': [1],
            'valuation_price': [1],
            'fx_rate': [0],
            'beginning_mv': [previous_leverage],
            'ending_mv': [previous_leverage + self.asset_df['base_margin_balance'].sum()],
            'unrealized_pnl': [0]
        })
        self.holding_df = pd.concat([self.holding_df, leverage_df], ignore_index=True)
        self.total_leverage = previous_leverage + self.asset_df['base_margin_balance'].sum()



    def cash_calculation(self):
        self.total_external_flow = self.transactions[self.transactions['sec_group'] == 'Cash']['net_cashflow'].sum()
        if self.previous_valuation.empty:
            previous_cashflow = 0.0
        else:
            previous_cashflow = self.previous_valuation[self.previous_valuation['type'] == 'Cash']['ending_mv'].sum()

        current_trade_cash = self.asset_df['base_cashflow'].sum()
        total_cash_flow = round(self.total_external_flow + current_trade_cash, 4) + previous_cashflow
        self.holding_df.loc[len(self.holding_df)] = {
            'transaction_id': '-',
            'instrument_name': 'Cash',
            'instrument_id': 'Cash',
            'group': 'Cash',
            'type': 'Cash',
            'currency': self.portfolio_data.currency,
            'trade_date': 0,
            'transaction_type': 'Cash',
            'beginning_pos': previous_cashflow,
            'ending_pos': float(total_cash_flow),
            'change': 0,
            'trade_price': 1,
            'valuation_price': 1,
            'fx_rate': 0,
            'beginning_mv': previous_cashflow,
            'ending_mv': float(total_cash_flow),
            'unrealized_pnl': 0
        }
        self.total_cash_flow = total_cash_flow
        self.holding_df['change'] = self.holding_df['ending_pos'] - self.holding_df['beginning_pos']

    def nav_calculation(self, calc_date, previous_date, portfolio_code):
        # # Previous NAV
        previous_nav = Nav.objects.filter(portfolio_code=portfolio_code, date=previous_date).values()
        if len(previous_nav) == 0:
            previous_nav = 0
        else:
            previous_nav = previous_nav[0]['total']

        # Total NAV
        total = previous_nav + self.total_external_flow + self.asset_df['realized_pnl'].sum()

        # Total Return Calculation
        if previous_nav != 0.0:
            period_return = (total - previous_nav - self.total_external_flow) / previous_nav
        else:
            period_return = 0.0

        total_asset_value = self.holding_df[(self.holding_df['type'] != 'Cash') & (self.holding_df['type'] != 'Leverage')]['ending_mv']

        if self.portfolio_data.calc_holding == True:
            asset_value = total_asset_value.sum() # -> Update
            cash_value = self.total_cash_flow
            liability = self.total_leverage
            h_nav = total_asset_value.sum() + self.total_cash_flow - self.total_leverage
        else:
            asset_value = 0.0
            cash_value = 0.0
            liability = 0.0
            h_nav = 0.0

        try:
            nav = Nav.objects.get(date=calc_date, portfolio_code=portfolio_code)
            nav.cash_val = cash_value
            nav.pos_val = asset_value
            nav.short_liab = liability
            nav.total = total
            nav.holding_nav = h_nav
            nav.period_return = round(period_return, 5)
            nav.save()
        except:
            Nav(date=calc_date,
                portfolio_code=portfolio_code,
                pos_val=asset_value,
                cash_val=cash_value,
                short_liab=liability,
                total=total,
                holding_nav=h_nav,
                period_return=round(period_return, 5)).save()

        self.response_list.append({'portfolio_code': portfolio_code,
                                   'date': calc_date,
                                   'process': 'Realized NAV Valuation',
                                   'exception': '-',
                                   'status': 'Completed',
                                   'comment': 'NAV ' + str(round(total, 2)) + ' ' + str(self.portfolio_data.currency)})

    def save_holding(self, trade_date, portfolio_code, holding_data):
        try:
            holding = Holding.objects.get(date=trade_date, portfolio_code=portfolio_code)
            holding.data = holding_data.to_json()
            holding.save()
        except:
            Holding(date=trade_date,
                    portfolio_code=portfolio_code,
                    data=holding_data.to_json()).save()

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
            print('Valuation Date', calc_date)
            previous_date = calc_date - timedelta(days=time_back)
            valuation.fetch_previous_valuation(previous_date=previous_date, portfolio_code=portfolio_code)
            if valuation.previous_valuation.empty and calc_date != valuation.portfolio_data.inception_date:
                valuation.add_error_message({'portfolio_code': portfolio_code,
                                             'date': calc_date,
                                             'process': 'Valuation',
                                             'exception': 'Missing Valuation',
                                             'status': 'Error',
                                             'comment': 'Missing valuation on ' + str(previous_date)})
                valuation.add_error_message({'portfolio_code': portfolio_code,
                                             'date': calc_date,
                                             'process': 'Valuation',
                                             'exception': 'Stopped Valuation',
                                             'status': 'Error',
                                             'comment': 'Valuation stopped due to missing previous valuation'})
                break
            valuation.calc_date = calc_date
            valuation.initialize_dataframe()
            valuation.load_fx_rates(trade_date=calc_date)
            valuation.fetch_transactions(trade_date=calc_date)
            valuation.asset_valuation()
            valuation.cash_calculation()
            valuation.leverage_calculation()

            valuation.save_holding(trade_date=calc_date,
                                   portfolio_code=portfolio_code,
                                   holding_data=valuation.holding_df)
            valuation.nav_calculation(calc_date=calc_date,
                                      previous_date=previous_date,
                                      portfolio_code=portfolio_code)
        calc_date = calc_date + timedelta(days=1)
    return valuation.send_responses()
