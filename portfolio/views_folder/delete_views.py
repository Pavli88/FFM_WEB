from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from portfolio.models import Transaction
import json
import pandas as pd
from app_functions.calculations import calculate_cash_holding


@csrf_exempt
def delete_transaction(request):
    if request.method == "POST":
        request_data = json.loads(request.body.decode('utf-8'))
        transactions = Transaction.objects.get(id=request_data['id']).delete()
        # portfolio_code = transactions.values()[0]['portfolio_code']
        # trade_date = transactions.values()[0]['trade_date']
        # currency = transactions.values()[0]['currency']
        # transactions.delete()
        # calculate_cash_holding(portfolio_code=portfolio_code,
        #                        start_date=trade_date,
        #                        currency=currency)
        return JsonResponse({'response': 'Transaction is deleted!'}, safe=False)
