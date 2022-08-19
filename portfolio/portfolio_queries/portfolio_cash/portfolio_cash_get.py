from django.db import connection
from django.http import JsonResponse


def get_port_total_cash_by_type(request, portfolio_code):
    if request.method == "GET":
        cursor = connection.cursor()
        query = """select transaction_type, sum(mv)
from portfolio_trade
where portfolio_code = '{portfolio_code}'
and (transaction_type = 'fee'
    or transaction_type = 'cash deposit'
    or transaction_type = 'cash withdrawal'
    or transaction_type = 'income'
    or transaction_type = 'dividend'
    or transaction_type = 'trading cost')
group by transaction_type;""".format(portfolio_code=portfolio_code)
        cursor.execute(query)
        row = cursor.fetchall()
        response = {}
        for record in row:
            response[record[0]] = record[1]
        print(response)
        return JsonResponse(list([response]), safe=False)


def get_port_daily_cash_flows(request):
    if request.method == "GET":
        cursor = connection.cursor()
        return JsonResponse(list([response]), safe=False)