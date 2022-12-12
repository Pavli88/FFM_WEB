from django.http import JsonResponse
from django.db import connection

import pandas as pd

# Model Imports
from robots.models import Balance, MonthlyReturns, Robots, RobotTrades


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
        cursor.execute("""set @sql = concat('select date, ', @sql, 'from robots_balance where date > "2022-01-01" group by date');""")
        cursor.execute("prepare stmt from @sql;")
        cursor.execute("execute stmt;")
        # cursor.execute("""deallocate prepare stmt;""")
        row = cursor.fetchall()
        df = pd.DataFrame(row, columns=[col[0] for col in cursor.description])
        data = []
        df['Total'] = df.iloc[:, 1:].sum(axis=1)
        for column in df.set_index('date'):
            data.append({'name': column, 'data': list(df[column].cumsum())})

        return JsonResponse({'dates': list(df['date']), 'data': data}, safe=False)
