import pandas as pd
from django.db import connection
from django.http import JsonResponse
from portfolio.models import Portfolio, CashFlow, Transaction, CashHolding, Holding
from app_functions.request_functions import *
from app_functions.calculations import calculate_transaction_pnl


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
        transactions = dynamic_mode_get(request_object=request.GET.items(),
                                             column_list=['id', 'portfolio_code', 'currency', 'transaction_type',
                                                          'trade_date__gte', 'trade_date__lte', 'is_active',
                                                          'security', ''],
                                             table=Transaction)
        df = pd.DataFrame(transactions)
        # df.loc[df.transaction_link_code == '', 'transaction_link_code'] = df['id']
        #
        # response = []
        # for i in df.to_dict('records'):
        #     print(type(i))
        return JsonResponse(transactions, safe=False)


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
from portfolio_transaction where sec_group='Cash' and portfolio_code = '{portfolio_code}' group by trade_date order by trade_date;
        """.format(portfolio_code=request.GET.get("portfolio_code")))

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


def available_cash(request):
    if request.method == "GET":
        try:
            cash_holding = CashHolding.objects.filter(portfolio_code=request.GET.get("portfolio_code")).order_by(
                'date').latest('date')
            response = {'currency': cash_holding.currency,
                        'amount': round(cash_holding.amount, 2),
                        'date': cash_holding.date}
        except:
            response = {'currency': '',
                        'amount': 0.0,
                        'date': ''}
        return JsonResponse(response, safe=False)


def transactions_pnls(request):
    if request.method == "GET":
        closed_transactions = Transaction.objects.filter(open_status='Closed', portfolio_code=request.GET.get("portfolio_code")).values_list('id', flat=True)
        for transaction in closed_transactions:
            calculate_transaction_pnl(transaction_id=transaction)
        cursor = connection.cursor()
        cursor.execute("""
                select inst.name, inst.group, inst.type, pt.transaction_type, pt.currency, pt.mv, pt.portfolio_code, tp.pnl
from portfolio_transactionpnl as tp, portfolio_transaction as pt, instrument_instruments as inst
where tp.transaction_id=pt.id and inst.id = tp.security and pt.portfolio_code='{portfolio_code}'
                """.format(portfolio_code=request.GET.get("portfolio_code")))

        row = cursor.fetchall()
        df = pd.DataFrame(row, columns=[col[0] for col in cursor.description])
        return JsonResponse(df.to_dict('records'), safe=False)


def get_holding(request):
    if request.method == "GET":
        try:
            holding_df = pd.read_json(Holding.objects.get(date=request.GET.get("date"), portfolio_code=request.GET.get("portfolio_code")).data)
            return JsonResponse(holding_df.to_dict('records'), safe=False)
        except Holding.DoesNotExist:
            return JsonResponse([{}], safe=False)
