import pandas as pd
from django.db import connection
from django.http import JsonResponse
from portfolio.models import Portfolio, CashFlow, Transaction
from app_functions.request_functions import *


def get_portfolios(request):
    if request.method == "GET":
        return JsonResponse(dynamic_mode_get(request_object=request.GET.items(),
                                             column_list=['portfolio_name', 'portfolio_type', 'currency', 'status',
                                                          'portfolio_code', 'owner', ''],
                                             table=Portfolio), safe=False)


def get_portfolio_transactions(request):
    if request.method == "GET":
        return JsonResponse(dynamic_mode_get(request_object=request.GET.items(),
                                             column_list=['id', 'portfolio_code', 'currency', 'transaction_type',
                                                          'trade_date__gte', 'trade_date__lte', 'is_active',
                                                          'security', ''],
                                             table=Transaction), safe=False)


def get_main_portfolio_cashflows(request):
    if request.method == "GET":
        records = CashFlow.objects.filter(portfolio_code=request.GET.get("portfolio_code")).values()
        df = pd.DataFrame(records).pivot_table(index='currency', columns='type', values='amount', aggfunc='sum').fillna(0).reset_index()
        return JsonResponse(df.to_dict('records'), safe=False)


def get_open_transactions(request):
    if request.method == "GET":
        print('test')
        cursor = connection.cursor()
        cursor.execute(
            """select *, if(pt.transaction_link_code='', pt.id, pt.transaction_link_code) as updated_id
from portfolio_transaction as pt
where pt.security != 'Cash' and pt.security != 'Margin'
and pt.transaction_link_code in (select id from portfolio_transaction where open_status = 'Open')
or pt.open_status = 'Open';"""
        )
        row = cursor.fetchall()
        df = pd.DataFrame(row, columns=[col[0] for col in cursor.description])
        transaction_codes = list(dict.fromkeys(df['updated_id'].tolist()))
        new_data_set = []
        for transaction_code in transaction_codes:
            df_transaction = df[df['updated_id'] == transaction_code]
            print(df_transaction)
            new_data_set.append({
                'id': df_transaction['updated_id'].tolist()[0],
                'portfolio_code': df_transaction['portfolio_code'].tolist()[0],
                'security': df_transaction['security'].tolist()[0],
                'sec_group': df_transaction['sec_group'].tolist()[0],
                'currency': df_transaction['currency'].tolist()[0],
                'transaction_type': df_transaction['transaction_type'].tolist()[0],
                'quantity': df_transaction['quantity'].sum(),
                'price': df_transaction['price'].tolist()[0],
                'mv': round(df_transaction['quantity'].sum() * df_transaction['price'].tolist()[0], 2),
                'account_id': df_transaction['account_id'].tolist()[0],
                'broker_id': df_transaction['broker_id'].tolist()[0],
            })
        return JsonResponse(new_data_set, safe=False)


def daily_cashflow_by_type(request):
    if request.method == "GET":
        cursor = connection.cursor()
        cursor.execute("""
        select trade_date,
       sum(case when transaction_type = 'Purchase Settlement' then mv else 0 end) as 'Purchase Settlement',
       sum(case when transaction_type = 'Sale Settlement' then mv else 0 end) as 'Sale Settlement',
       sum(case when transaction_type = 'Subscription' then mv else 0 end) as 'Subscription',
       sum(case when transaction_type = 'Redemption' then mv else 0 end) as 'Redemption'
from portfolio_transaction where sec_group='Cash' group by trade_date order by trade_date;
        """)

        row = cursor.fetchall()
        df = pd.DataFrame(row, columns=[col[0] for col in cursor.description])

        series = []
        for column in df:
            print(column)
            if column == 'trade_date':
                pass
            else:
                series.append({'name': column, 'data': df[column].tolist()})

        return JsonResponse({
            'dates': df['trade_date'].tolist(),
            'series': series
        }, safe=False)
