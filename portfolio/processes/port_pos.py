from portfolio.models import *
import pandas as pd
import datetime
import numpy as np
from datetime import timedelta
from mysite.my_functions.general_functions import *
from django.db import connection


def portfolio_positions(portfolio_code, start_date):
    date = datetime.datetime.strptime(str(start_date), '%Y-%m-%d')
    curent_date = get_today()
    cursor = connection.cursor()
    query = """select
       date,
       sum(quantity) as aggregated_quantity,
       security
from portfolio_trade
where portfolio_code = '{portfolio_code}'
and (transaction_type = 'purchase' or transaction_type = 'sale'
and date >= '{start_date}') group by date, security;""".format(portfolio_code=portfolio_code, start_date=date)

    cursor.execute(query)
    df = pd.DataFrame(cursor.fetchall()).rename(columns={0: 'date',
                                                         1: 'quantity',
                                                         2: 'security',
                                                         })
    securities_list = list(dict.fromkeys(list(df['security'])))
    for security in securities_list:
        beginning_date = start_date
        filtered_df = df[df['security']==security]
        start_value = 0.0
        start_df = pd.DataFrame({'date': beginning_date, 'quantity': start_value, 'security': security}, index=[0])
        while beginning_date <= curent_date:
            second_filtered_df = filtered_df[(filtered_df['date']==beginning_date) & (filtered_df['security'] == security)]
            if second_filtered_df.empty:
                pass
            else:
                start_value = start_value + list(second_filtered_df['quantity'])[0]
            start_df = start_df.append({'date': beginning_date, 'quantity': start_value, 'security': security},
                                           ignore_index=True)
            beginning_date = beginning_date + timedelta(days=1)
        for index, row in start_df.iterrows():
            try:
                existing_position_record = Positions.objects.get(portfolio_name=portfolio_code,
                                                                 security=int(row['security']),
                                                                 date=row['date'])
                if row['quantity'] == 0:
                    existing_position_record.delete()
                else:
                    existing_position_record.quantity = row['quantity']
                    existing_position_record.save()
            except Positions.DoesNotExist:
                if row['quantity'] == 0:
                    pass
                else:
                    Positions(portfolio_name=portfolio_code,
                              security=int(row['security']),
                              quantity=row['quantity'],
                              date=row['date']).save()

        print(start_df)
    response = ''
    return response
