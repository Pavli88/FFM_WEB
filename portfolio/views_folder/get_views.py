import json
import numpy as np
import pandas as pd
from django.db import connection
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from portfolio.models import Portfolio, Transaction, Holding, Nav, TradeRoutes, PortGroup
from app_functions.request_functions import *
from app_functions.calculations import calculate_transaction_pnl, drawdown_calc
from calculations.processes.valuation.valuation import calculate_holdings

def get_portfolios(request):
    if request.method == "GET":
        filters = {key: value for key, value in request.GET.items() if value}

        try:
            portfolios = Portfolio.objects.filter(**filters).values()
            portfolios_list = list(portfolios)
            return JsonResponse(portfolios_list, safe=False, status=200)

        except Exception as e:
            # Handle errors, such as invalid filters
            return JsonResponse({"error": str(e)}, status=400)

        # Return bad request if method is not GET
    return JsonResponse({"error": "Invalid request method"}, status=405)


@csrf_exempt
def get_portfolio_transactions(request):
    if request.method == "POST":
        request_body = json.loads(request.body.decode('utf-8'))
        print(request_body)
        filters = {}
        for key, value in request_body.items():
            if isinstance(value, list):
                print('MULTIPLE')
                if len(value) > 0:
                    filters[key + '__in'] = value
            else:
                print('GROUP')
                filters[key] = value

        results = Transaction.objects.select_related('security').all().filter(**filters) ##.values()

        l = []
        for transaction in results:
            l.append({
                'id': transaction.id,
                'transaction_link_code': transaction.transaction_link_code,
                'name': transaction.security.name,
                'security_id': transaction.security_id,
                'portfolio_code': transaction.portfolio_code,
                'transaction_type': transaction.transaction_type,
                'currency': transaction.currency,
                'open_status': transaction.open_status,
                'is_active': transaction.is_active,
                'quantity': transaction.quantity,
                'price': transaction.price,
                'fx_rate': transaction.fx_rate,
                'mv': transaction.mv,
                'local_mv': transaction.local_mv,
                'net_cashflow': transaction.net_cashflow,
                'local_cashflow': transaction.local_cashflow,
                'margin_balance': transaction.margin_balance,
                'margin_rate': transaction.margin_rate,
                'account_id': transaction.account_id,
                'broker_id': transaction.broker_id,
                'broker': transaction.broker,
                'trade_date': transaction.trade_date,
                'settlement_date': transaction.settlement_date,
                'option': transaction.option,
                'bv': transaction.bv,
                'local_bv': transaction.local_bv
            })
        return JsonResponse(l, safe=False)


def get_open_transactions(request):
    if request.method == "GET":
        print('test')
        results = Transaction.objects.select_related('security').all().filter(is_active=1)
        print(results)
        l = []
        for transaction in results:
            l.append({
                'id': transaction.id,
                'portfolio_code': transaction.portfolio_code,
                'name': transaction.security.name,
                'security_id': transaction.security_id,
                'sec_group': transaction.security.group,
                'currency': transaction.currency,
                'transaction_type': transaction.transaction_type,
                'quantity': transaction.quantity,
                'price': transaction.price,
                'mv': transaction.mv,
                'account_id': transaction.account_id,
                'broker_id': transaction.broker_id,
                'broker': transaction.broker,
                'trade_date': transaction.trade_date,
            })
        return JsonResponse(l, safe=False)


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
                          select sum(pnl) as total, sum(cost) as cost, portfolio_code
from portfolio_nav
group by portfolio_code order by total desc;
""")

        row = cursor.fetchall()
        df = pd.DataFrame(row, columns=[col[0] for col in cursor.description])
        df['net_pnl'] = df['total'] + df['cost']
        print(df)
        return JsonResponse(df.to_dict('records'), safe=False)


def transactions_pnls(request):
    if request.method == "GET":
        transactions = Transaction.objects.filter(portfolio_code=request.GET.get("portfolio_code"),
                                                  transaction_link_code__gt=0,
                                                  is_active=0).values()
        return JsonResponse(list(transactions), safe=False)


def get_holding(request):
    if request.method == "GET":
        holdings = Holding.objects.select_related('instrument').filter(date=request.GET.get("date")).filter(portfolio_code=request.GET.get("portfolio_code"))
        holdings_list = [
            {
                'portfolio_code': holding.portfolio_code,
                'date': holding.date,
                'trd_id': holding.id,
                'inv_num': holding.inv_num,
                'trade_date': holding.trade_date,
                'trade_type': holding.trade_type,
                'instrument_id': holding.instrument_id,
                'name': holding.instrument.name,
                'group': holding.instrument.group,
                'type': holding.instrument.type,
                'currency': holding.instrument.currency,
                'quantity': holding.quantity,
                'trade_price': round(holding.trade_price, 4),
                'market_price': round(holding.market_price, 4),
                'fx_rate': round(holding.fx_rate,  4),
                'mv': holding.mv,
                'bv': holding.bv,
                'weight': holding.weight,
                'ugl': holding.ugl,
                'rgl': holding.rgl,
            }
            for holding in holdings
        ]
        return JsonResponse(pd.DataFrame(holdings_list).to_dict('records'), safe=False)

def get_exposures(request):
    if request.method == "GET":
        try:
            # responses = calculate_holdings(portfolio_code=request.GET.get("portfolio_code"), calc_date=request.GET.get("date"))
            # print(responses)
            stress_percentage = float(request.GET.get("stress_percentage")) / 100
            holding_df = pd.read_json(Holding.objects.get(date=request.GET.get("date"), portfolio_code=request.GET.get("portfolio_code")).data)
            nav = Nav.objects.filter(portfolio_code=request.GET.get("portfolio_code"), date=request.GET.get("date")).values()[0]['total']
            holding_df['contribution'] = (holding_df['unrealized_pnl'] / nav) * 100
            holding_df['ticked'] = False
            holding_df['sim_price'] = np.where(holding_df['transaction_type'] == 'Purchase', holding_df['valuation_price'] * (1 - stress_percentage), holding_df['valuation_price'] * (1 + stress_percentage))
            holding_df['sim_profit'] = np.where(holding_df['transaction_type'] == 'Purchase', (holding_df['sim_price'] - holding_df['trade_price']) * holding_df['ending_pos'] * holding_df['fx_rate'], (holding_df['trade_price'] - holding_df['sim_price']) * holding_df['ending_pos'] * holding_df['fx_rate'])
            holding_df['sim_contr'] = (holding_df['sim_profit'] / nav) * 100
            holding_df['sim_contr_amended'] = (holding_df['sim_profit'] / nav) * 100
            holding_df['sensitivity'] = abs(holding_df['sim_contr']) - abs(holding_df['contribution'])
            holding_df = holding_df[(holding_df['ending_mv'] > 0.0) & (holding_df['instrument_name'] != 'Cash')].round(
                {'ending_mv': 1,
                 'base_leverage': 1,
                 'unrealized_pnl': 2,
                 'fx_rate': 2,
                 'trade_price': 4,
                 'valuation_price': 4,
                 'contribution': 2,
                 'sim_contr': 2,
                 'sim_profit': 2,
                 'sim_price': 2,
                 'sensitivity': 2,
                 'sim_contr_amended': 2
                 })
            total_sim_profit = holding_df['sim_profit'].sum()
            sim_nav = round(nav + total_sim_profit, 2)
            sim_drawdown = round((nav - sim_nav) / nav, 3) * -100

            return JsonResponse({
                'data': holding_df.to_dict('records'),
                'nav': round(nav, 2),
                'sim_nav': sim_nav,
                'sim_dd': round(sim_drawdown, 2)
            }, safe=False)
        except Holding.DoesNotExist:
            return JsonResponse({'data': [], 'nav': 0.0}, safe=False)


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


def get_monthly_pnl(request):
    if request.method == "GET":
        cursor = connection.cursor()
        cursor.execute("""
                select sum(pnl) as pnl, any_value(date) as date from portfolio_nav group by year(date), month(date);""")

        row = cursor.fetchall()
        df = pd.DataFrame(row, columns=[col[0] for col in cursor.description])
        return JsonResponse(df.to_dict('records'), safe=False)


def get_historic_nav(request):
    if request.method == "GET":
        cursor = connection.cursor()
        cursor.execute("""
        select pn.date, sum(pn.holding_nav) as holding_nav, sum(pn.total) as total
from portfolio_nav as pn,
     portfolio_portfolio as p
where p.portfolio_code = pn.portfolio_code
  and p.portfolio_type = 'Automated'
group by pn.date
order by pn.date asc;
        """)

        row = cursor.fetchall()
        df = pd.DataFrame(row, columns=[col[0] for col in cursor.description])
        df['diff'] = df['holding_nav'] - df['total']
        df['drawdown'] = (df['diff'] / df['total']) * 100
        df = df.fillna(0)
        return JsonResponse(df.to_dict('records'), safe=False)


@require_GET
def get_port_groups(request):
    port_groups = PortGroup.objects.select_related('portfolio').all()
    print(port_groups)
    g = []
    for group in port_groups:
        g.append({
            'id': group.id,
            'name': group.portfolio.portfolio_name,
            'parent_id': group.parent_id,
            'portfolio_code': group.portfolio.portfolio_code,
            'portfolio_type': group.portfolio.portfolio_type,
        })
    return JsonResponse(g, safe=False, status=200)
    # try:
    #
    #
    # except Exception as e:
    #     return JsonResponse({'error': str(e)}, status=500)