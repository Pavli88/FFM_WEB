from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from portfolio.models import Transaction
import json
import pandas as pd
from app_functions.calculations import calculate_holdings


@csrf_exempt
def delete_transaction(request):
    if request.method == "POST":
        request_data = json.loads(request.body.decode('utf-8'))
        transaction = Transaction.objects.get(id=request_data['id'])
        transaction.delete()
        linked_transactions = Transaction.objects.filter(transaction_link_code=request_data['id'])
        for tr in linked_transactions:
            tr.delete()
        # calculate_holdings(portfolio_code=transaction.portfolio_code, calc_date=transaction.trade_date)
        return JsonResponse({'response': 'Transaction is deleted!'}, safe=False)
