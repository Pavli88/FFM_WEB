from django.db import connection
from django.http import JsonResponse

# Model imports
from portfolio.models import CashHolding


def get_port_total_cash_by_type(request, portfolio_code):
    if request.method == "GET":
        cursor = connection.cursor()
        query = """select transaction_type, sum(mv) as mv
from portfolio_trade as pt, instrument_instruments as inst
where pt.security = inst.id
      and pt.portfolio_code = '{portfolio_code}'
and (pt.transaction_type = 'fee'
    or pt.transaction_type = 'cash deposit'
    or pt.transaction_type = 'cash withdrawal'
    or pt.transaction_type = 'income'
    or pt.transaction_type = 'dividend'
    or pt.transaction_type = 'trading cost')
and inst.currency = '{currency}'
group by pt.transaction_type""".format(portfolio_code=portfolio_code, currency='HUF')
        cursor.execute(query)
        row = cursor.fetchall()
        response = []
        id = 0
        for record in row:
            response.append({'id': id, 'name': record[0], 'value': record[1]})
            id = id + 1
        return JsonResponse(response, safe=False)


def get_port_daily_cash_flows(request):
    if request.method == "GET":
        cursor = connection.cursor()
        response = ''
        return JsonResponse(list([response]), safe=False)


def get_cash_holding_by_date(request, date):
    if request.method == "GET":
        portfolio_code = request.GET.get('portfolio_code')
        print(portfolio_code)
        cash_holding_data = CashHolding.objects.filter(date=date).filter(portfolio_code=portfolio_code).values()
        print(cash_holding_data)
        return JsonResponse(list(cash_holding_data), safe=False)