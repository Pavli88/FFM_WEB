# Django imports
from django.http import JsonResponse
from django.db import connection

# General Functions
from mysite.my_functions.general_functions import *

import pandas as pd

def all_daily_returns(request):
    if request.method == "GET":
        cursor = connection.cursor()
        cursor.execute("""select date, round((sum(rb.realized_pnl)/sum(rb.opening_balance))*100, 2) as total_return,
       round(sum(rb.realized_pnl), 2) as total_pnl
from robots_balance rb, robots_robots as r
where rb.robot_id=r.id
and r.env='{env}'
and r.status='active'
and rb.date >= '{date}'
group by rb.date;""".format(date=request.GET.get("date"), env=request.GET.get("env")))
        row = cursor.fetchall()
        df = pd.DataFrame(row, columns=[col[0] for col in cursor.description])

        return JsonResponse({'dates': list(df['date']), 'total_returns': list(df['total_return']), 'pnls': list(df['total_pnl'])}, safe=False)