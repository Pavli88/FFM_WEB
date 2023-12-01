import json
import numpy as np
import pandas as pd
from django.db import connection
from django.http import JsonResponse
from portfolio.models import Portfolio, Transaction, Holding, Nav, TradeRoutes
from app_functions.request_functions import *
from app_functions.calculations import calculate_transaction_pnl, drawdown_calc
from calculations.processes.valuation.valuation import calculate_holdings

def get_portfolios(request):
    if request.method == "GET":
        for i in request.GET.items():
            print(i)
        return JsonResponse(dynamic_mode_get(request_object=request.GET.items(),
                                             column_list=['portfolio_name', 'portfolio_type', 'currency', 'status',
                                                          'portfolio_code', 'owner', ''],
                                             table=Portfolio), safe=False)


def get_portfolio_transactions(request):
    if request.method == "GET":

        # filters = {}
        # for key, value in request.GET.items():
        #     if value == '':
        #         pass
        #     else:
        #         if key in ['id', 'portfolio_code', 'currency', 'transaction_type',
        #                                              'trade_date__gte', 'trade_date__lte', 'is_active',
        #                                              'security', '']:
        #             filters[key] = value
        # results = Transaction.objects.filter(**filters).select_related('security').values()
        # print(results)
        # df = pd.DataFrame(results)
        # print(df)
        transactions = dynamic_mode_get(request_object=request.GET.items(),
                                        column_list=['id', 'portfolio_code', 'currency', 'transaction_type',
                                                     'trade_date__gte', 'trade_date__lte', 'is_active',
                                                     'security', ''],
                                        table=Transaction)


        # security_codes = list(dict.fromkeys(df['security']))

        # df.loc[df.transaction_link_code == '', 'transaction_link_code'] = df['id']
        #
        # response = []
        # for i in df.to_dict('records'):
        #     print(type(i))
        return JsonResponse(transactions, safe=False)


def get_open_transactions(request):
    if request.method == "GET":
        print('test')
        cursor = connection.cursor()
        cursor.execute(
            """select pt.id, pt.portfolio_code,
       inst.name, pt.sec_group, pt.security,
       pt.currency, pt.transaction_type,
       pt.quantity, pt.price, pt.account_id, pt.broker_id, if(pt.transaction_link_code='', pt.id, pt.transaction_link_code) as updated_id
from portfolio_transaction as pt, instrument_instruments as inst
where pt.transaction_link_code in (select id from portfolio_transaction where is_active = 1)
or pt.is_active = 1
and pt.sec_group != 'Cash'
and pt.security = inst.id;"""
        )
        row = cursor.fetchall()
        df = pd.DataFrame(row, columns=[col[0] for col in cursor.description])
        transaction_codes = list(dict.fromkeys(df['updated_id'].tolist()))
        new_df = pd.DataFrame({'id': [],
                               'portfolio_code': [],
                               'name': [],
                               'security': [],
                               'sec_group': [],
                               'currency': [],
                               'transaction_type': [],
                               'quantity': [],
                               'price': [],
                               'mv': [],
                               'account_id': [],
                               'broker_id': []})
        for transaction_code in transaction_codes:
            df_transaction = df[df['updated_id'] == transaction_code]

            new_df.loc[len(new_df.index)] = [
                df_transaction['updated_id'].tolist()[0],
                df_transaction['portfolio_code'].tolist()[0],
                df_transaction['name'].tolist()[0],
                df_transaction['security'].tolist()[0],
                df_transaction['sec_group'].tolist()[0],
                df_transaction['currency'].tolist()[0],
                df_transaction['transaction_type'].tolist()[0],
                df_transaction['quantity'].sum(),
                df_transaction['price'].tolist()[0],
                round(df_transaction['quantity'].sum() * df_transaction['price'].tolist()[0], 2),
                df_transaction['account_id'].tolist()[0],
                df_transaction['broker_id'].tolist()[0],
            ]
        return JsonResponse(new_df.to_json(orient='records'), safe=False)


def daily_cashflow_by_type(request):
    if request.method == "GET":
        cursor = connection.cursor()
        cursor.execute("""
        select trade_date,
       sum(case when transaction_type = 'Subscription' then net_cashflow else 0 end) as 'Subscription',
       sum(case when transaction_type = 'Redemption' then net_cashflow else 0 end) as 'Redemption',
       sum(case when transaction_type = 'Commission' then net_cashflow else 0 end) as 'Commission'
from portfolio_transaction where sec_group='Cash' and portfolio_code = '{portfolio_code}' group by trade_date order by trade_date;
        """.format(portfolio_code=request.GET.get("portfolio_code")))

        row = cursor.fetchall()
        df = pd.DataFrame(row, columns=[col[0] for col in cursor.description])
        series = []
        for column in df:
            if column == 'trade_date':
                pass
            else:
                series.append({'name': column, 'data': df[column].tolist()})

        return JsonResponse({
            'dates': df['trade_date'].tolist(),
            'series': series
        }, safe=False)


def get_nav(request):
    if request.method == "GET":
        navs = dynamic_mode_get(request_object=request.GET.items(),
                                column_list=['date', 'date__gte', 'portfolio_code'],
                                table=Nav)
        return JsonResponse(pd.DataFrame(navs).sort_values(by=['date']).to_dict('records'), safe=False)


def get_portfolio_nav(request):
    if request.method == "GET":
        cursor = connection.cursor()
        cursor.execute("""
                        select pn.total, pp.portfolio_code, pp.currency 
                        from portfolio_nav as pn, portfolio_portfolio as pp
                        where pn.portfolio_code = pp.portfolio_code and pn.date = '{date}'
                        order by pn.total desc;
                        """.format(date=request.GET.get("date")))

        row = cursor.fetchall()
        df = pd.DataFrame(row, columns=[col[0] for col in cursor.description])
        return JsonResponse(df.to_dict('records'), safe=False)


def get_portfolio_nav_grouped(request):
    if request.method == "GET":
        cursor = connection.cursor()
        cursor.execute("""
                        select sum(pn.total) as total, pp.portfolio_type
from portfolio_nav as pn, portfolio_portfolio as pp
where pn.portfolio_code = pp.portfolio_code
and pn.date = '{date}'
group by pp.portfolio_type
order by total desc;
                        """.format(date=request.GET.get("date")))

        row = cursor.fetchall()
        df = pd.DataFrame(row, columns=[col[0] for col in cursor.description])
        return JsonResponse(df.to_dict('records'), safe=False)


def get_total_pnl(request):
    if request.method == "GET":
        cursor = connection.cursor()
        cursor.execute("""
                          select sum(realized_pnl) as total, portfolio_code
from portfolio_transaction
group by portfolio_code;
""")

        row = cursor.fetchall()
        df = pd.DataFrame(row, columns=[col[0] for col in cursor.description])
        return JsonResponse(df.to_dict('records'), safe=False)


def transactions_pnls(request):
    if request.method == "GET":
        transactions = Transaction.objects.filter(portfolio_code=request.GET.get("portfolio_code"),
                                                  transaction_link_code__gt=0,
                                                  is_active=0).values()
        return JsonResponse(list(transactions), safe=False)


def get_holding(request):
    if request.method == "GET":
        print("GET PORTHOLDING")
        try:
            holding_df = pd.read_json(Holding.objects.get(date=request.GET.get("date"), portfolio_code=request.GET.get("portfolio_code")).data)
            return JsonResponse(holding_df.to_dict('records'), safe=False)
        except Holding.DoesNotExist:
            return JsonResponse([{}], safe=False)


def aggregated_security_pnl(request):
    if request.method == "GET":

        cursor = connection.cursor()
        cursor.execute("""
                select inst.name, inst.group, inst.type, pt.realized_pnl 
from portfolio_transaction as pt, instrument_instruments as inst
       where pt.security=inst.id
         and pt.trade_date >= '{start_date}'
and pt.portfolio_code='{portfolio_code}'
and inst.group != 'Cash';
                """.format(portfolio_code=request.GET.get("portfolio_code"),
                           start_date=request.GET.get("start_date")))

        row = cursor.fetchall()
        df = pd.DataFrame(row, columns=[col[0] for col in cursor.description])

        pnl_by_name = df.groupby(['name']).sum().reset_index()[['name', 'realized_pnl']].sort_values(by='realized_pnl', ascending=False)
        pnl_by_group = df.groupby(['group']).sum().reset_index()[['group', 'realized_pnl']]
        pnl_by_type = df.groupby(['type']).sum().reset_index()[['type', 'realized_pnl']]
        return JsonResponse({'by_name': pnl_by_name.to_dict('records'),
                              'by_group': pnl_by_group.to_dict('records'),
                              'by_type': pnl_by_type.to_dict('records')
                              }, safe=False)


def get_exposures(request):
    if request.method == "GET":
        try:
            # responses = calculate_holdings(portfolio_code=request.GET.get("portfolio_code"), calc_date=request.GET.get("date"))
            # print(responses)
            holding_df = pd.read_json(Holding.objects.get(date=request.GET.get("date"), portfolio_code=request.GET.get("portfolio_code")).data)
            nav = Nav.objects.filter(portfolio_code=request.GET.get("portfolio_code"), date=request.GET.get("date")).values()[0]['total']
            holding_df['contribution'] = (holding_df['unrealized_pnl'] / nav) * 100
            holding_df = holding_df[(holding_df['ending_mv'] > 0.0) & (holding_df['instrument_name'] != 'Cash')].round({'ending_mv': 1,
                                                                            'base_leverage': 1,
                                                                            'unrealized_pnl': 2,
                                                                            'fx_rate': 2,
                                                                            'trade_price': 4,
                                                                            'valuation_price': 4,
                                                                            'contribution': 2})
            return JsonResponse({'data': holding_df.to_dict('records'), 'nav': round(nav, 2)}, safe=False)
        except Holding.DoesNotExist:
            return JsonResponse([{}], safe=False)


def get_drawdown(request):
    if request.method == "GET":
        portfolio_daily_returns = pd.DataFrame(Nav.objects.filter(portfolio_code=request.GET.get("portfolio_code"),
                                                     date__gte=request.GET.get("start_date")).values())
        drawdown_list = drawdown_calc(data_series=portfolio_daily_returns['period_return'])
        return JsonResponse({
            'dates': list(portfolio_daily_returns['date']),
            'data': drawdown_list
        }, safe=False)


def get_perf_dashboard(request):
    if request.method == "GET":
        cursor = connection.cursor()
        cursor.execute("""select p.portfolio_name, p.currency, pt.period, pt.total_return from portfolio_totalreturn as pt, portfolio_portfolio as p
where pt.portfolio_code = p.portfolio_code
and pt.end_date='{date}';""".format(date=request.GET.get("date")))

        row = cursor.fetchall()
        df = pd.DataFrame(row, columns=[col[0] for col in cursor.description])
        df['total_return'] = df['total_return'] * 100
        df = df.pivot_table('total_return',
                            ['portfolio_name'],
                            'period').reset_index().fillna(0.0)
        return JsonResponse(df.to_dict('records'), safe=False)


def get_trade_routes(request):
    if request.method == "GET":
        cursor = connection.cursor()
        cursor.execute("""
        select pt.id,
       pt.is_active,
       pt.quantity,
       pt.broker_account_id,
       pt.inst_id,
       instrument_instruments.name,
       source_ticker, source,
       broker_name,
       account_number from portfolio_traderoutes as pt
inner join instrument_instruments on pt.inst_id = instrument_instruments.id
inner join instrument_tickers on pt.ticker_id = instrument_tickers.id
inner join accounts_brokeraccounts on pt.broker_account_id = accounts_brokeraccounts.id
where pt.portfolio_code = '{portfolio_code}';
        """.format(portfolio_code=request.GET.get("portfolio_code")))

        row = cursor.fetchall()
        df = pd.DataFrame(row, columns=[col[0] for col in cursor.description])

        return JsonResponse(df.to_dict('records'), safe=False)