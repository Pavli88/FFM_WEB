from django.http import JsonResponse
from django.db import connection
from django.db.models import Sum

import pandas as pd

# Model Imports
from robots.models import Balance, MonthlyReturns, Robots, RobotTrades, Strategy
from accounts.models import BrokerAccounts

# Process imports
from mysite.processes.risk_calculations import drawdown_calc
from mysite.processes.oanda import OandaV20


def get_robots_by_strategy_id(request):
    print('strategy id')
    if request.method == "GET":
        cursor = connection.cursor()
        cursor.execute("select*from robots_robots where strategy_id in ('ICA', 'Position');")
        row = cursor.fetchall()
        df = pd.DataFrame(row, columns=[col[0] for col in cursor.description])
        print(df)
        return JsonResponse(list(), safe=False)


def get_strategies(request):
    if request.method == "GET":
        return JsonResponse(list(Strategy.objects.filter().values()), safe=False)


def get_robot(request, id):
    if request.method == "GET":
        print(id)
        return JsonResponse(list(Robots.objects.filter(id=id).values()), safe=False)


def get_robots(request, env):
    if request.method == "GET":
        return JsonResponse(list(Robots.objects.filter(env=env).values()), safe=False)


def get_active_robots(request, env):
    if request.method == "GET":
        return JsonResponse(list(Robots.objects.filter(env=env, status='active').values()), safe=False)


def get_robot_balance(request):
    if request.method == "GET":
        return JsonResponse(
            list(Balance.objects.filter(robot_id=request.GET.get("id")).filter(date__gte=request.GET.get("start_date")).values()),
            safe=False)


def monthly_returns(request):
    if request.method == 'GET':
        monthly_returns = MonthlyReturns.objects.filter(robot_id=request.GET.get('robot_id'), date__gte=request.GET.get('date') + '-01').order_by('date').values()
        return JsonResponse(list(monthly_returns), safe=False)


def transactions(request):
    if request.method == "GET":
        return JsonResponse(list(RobotTrades.objects.filter(robot=request.GET.get("robot_id")).filter(
            close_time__gte=request.GET.get("start_date")).filter(
            close_time__lte=request.GET.get("end_date")).values()), safe=False)


def all_pnl_series(request):
    if request.method == "GET":
        print(request.GET.get("date"))
        cursor = connection.cursor()
        cursor.execute("set @sql = null;")
        cursor.execute("""
        select group_concat(distinct
                    concat(' sum(if(robot_id = ', id, ', realized_pnl, 0)) as "', name, '"')
           )
into @sql
from robots_robots
where status = %s
and env=%s;
        """, ['active', 'live'])
        cursor.execute("""set @sql = concat('select date, ', @sql, 'from robots_balance where date > "{reporting_date}" group by date');""".format(reporting_date=request.GET.get("date")))
        cursor.execute("prepare stmt from @sql;")
        cursor.execute("execute stmt;")
        row = cursor.fetchall()
        df = pd.DataFrame(row, columns=[col[0] for col in cursor.description])
        data = []
        df['Total'] = df.iloc[:, 1:].sum(axis=1)
        for column in df.set_index('date'):
            data.append({'name': column, 'data': list(df[column].cumsum())})

        return JsonResponse({'dates': list(df['date']), 'data': data}, safe=False)


def all_robots_drawdown(request):
    cursor = connection.cursor()
    cursor.execute("""select date, round((sum(rb.realized_pnl)/sum(rb.opening_balance)), 2) as total_return
    from robots_balance rb, robots_robots as r
    where rb.robot_id=r.id
    and r.env='{env}'
    and r.status='active'
    and rb.date >= '{date}'
    group by rb.date;""".format(date=request.GET.get("date"), env=request.GET.get("env")))
    row = cursor.fetchall()
    df = pd.DataFrame(row, columns=[col[0] for col in cursor.description])
    drawdown = drawdown_calc(data_series=list(df['total_return']))
    print(drawdown)
    return JsonResponse({'dates': list(df['date']), 'drawdown': drawdown}, safe=False)


def get_robot_exposures(request):
    if request.method == "GET":
        cursor = connection.cursor()
        cursor.execute("""
        select robots_robottrades.robot,
       robots_robottrades.quantity,
       robots_robottrades.open_price,
       robots_robots.name,
       robots_robots.strategy,
       robots_robots.security,
       risk_robotrisk.quantity_type,
       risk_robotrisk.risk_per_trade,
       abs(robots_robottrades.quantity*robots_robottrades.open_price) as mv,
       rb.close_balance
from robots_robottrades
    join robots_robots on robots_robottrades.robot = robots_robots.id
    join risk_robotrisk on risk_robotrisk.robot = robots_robots.id
join (select*from robots_balance where date='{date}') as rb on robots_robottrades.robot = rb.robot_id
       where robots_robottrades.status = 'OPEN'
and robots_robots.status='active'
and robots_robots.env='{env}';
        """.format(date=request.GET.get("date"), env='live'))
        row = cursor.fetchall()
        df = pd.DataFrame(row, columns=[col[0] for col in cursor.description])
        securities = list(df['security'].drop_duplicates())
        print(securities)
        total_balance = Balance.objects.filter(date=request.GET.get("date")).aggregate(Sum('close_balance'))


        # This part needs to be updated with a working soluton
        broker = BrokerAccounts.objects.values()
        api_connection = OandaV20(access_token=broker[0]['access_token'],
                                  account_id=broker[0]['account_number'],
                                  environment=broker[0]['env'])
        prices = api_connection.get_prices_2(instruments=','.join(securities))
        price_dict = {}
        for price in prices:
            # print(price)
            print(price['bids'][0]['price'], price['asks'][0]['price'], price['instrument'])
            price_dict[price['instrument']] = (float(price['bids'][0]['price']) + float(price['asks'][0]['price']))/2
        print(price_dict)

        ###################################################################

        df['current_price'] = df['security'].map(price_dict)
        df['current_mv'] = abs(df['quantity']*df['current_price'])
        pnl = df['current_mv']-df['mv']
        df['pnl'] = round(pnl.where(df['quantity'] > 0, other=pnl*-1), 2)
        df['ret'] = round((df['pnl']/df['close_balance'])*100, 2)
        df['ret_to_total'] = round((df['pnl']/total_balance['close_balance__sum'])*100, 2)
        aggregated_df = df.groupby('name').sum().reset_index()
        aggregated_df['avg_price'] = round(abs(aggregated_df['mv']/aggregated_df['quantity']), 2)
        # counter = grouper.count()
        # counter['pnl'] = grouper.pnl.sum()
        # counter['current_mv'] = grouper.current_mv.sum()
        # counter['mv'] = grouper.mv.sum()
        # counter['close_balance'] = grouper.close_balance.sum()
        # counter = counter.reset_index()
        # counter['avg_price'] = counter['close_balance']/counter['robot']
        print(df)
        print(aggregated_df[['name', 'quantity', 'pnl', 'ret', 'ret_to_total', 'avg_price']])
        # print(df.groupby('name')['pnl', 'current_mv'].agg(['sum', 'count']))
        # print(df.groupby(['name']).count())
        response = {'name': aggregated_df['name'].tolist(),
                    'quanity': aggregated_df['quantity'].tolist(),
                    'pnl': aggregated_df['pnl'].tolist(),
                    'ret': aggregated_df['ret'].tolist(),
                    'ret_to_total': aggregated_df['ret_to_total'].tolist(),
                    'avg_price': aggregated_df['avg_price'].tolist()
                    }
        print(response)
        return JsonResponse(response, safe=False)