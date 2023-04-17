import pandas as pd

from django.http import JsonResponse

# Model Imports
from portfolio.models import Portfolio, CashFlow, Transaction


def get_portfolios(request):
    if request.method == "GET":
        print('PORT')
        filters = {}
        for key, value in request.GET.items():
            if key in ['portfolio_name', 'portfolio_type', 'currency', 'status', 'portfolio_code', 'owner', '']:
                filters[key] = value
        return JsonResponse(list(Portfolio.objects.filter(**filters).values()), safe=False)


def get_main_portfolio_cashflows(request):
    if request.method == "GET":
        records = CashFlow.objects.filter(portfolio_code=request.GET.get("portfolio_code")).values()
        df = pd.DataFrame(records).pivot_table(index='currency', columns='type', values='amount', aggfunc='sum').fillna(0).reset_index()
        print(df.to_dict('records'))
        return JsonResponse(df.to_dict('records'), safe=False)


def get_portfolio_transactions(request):
    print('PORTFOLIO TRANSACTIONS')
    if request.method == "GET":
        filters = {}
        for key, value in request.GET.items():
            if key in ['id', 'portfolio_code', 'currency', 'transaction_type', 'trade_date', 'is_active', 'security', '']:
                filters[key] = value
        return JsonResponse(list(Transaction.objects.filter(**filters).values()), safe=False)