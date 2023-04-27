from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from portfolio.models import Transaction
import json
import pandas as pd


@csrf_exempt
def delete_transaction(request):
    if request.method == "POST":
        request_data = json.loads(request.body.decode('utf-8'))
        transactions = Transaction.objects.filter(
            Q(id=request_data['id']) | Q(transaction_link_code__in=Transaction.objects.filter(
                Q(id=request_data['id']) | Q(transaction_link_code=request_data['id'])).values_list('id', flat=True)))

        # Update total cash values as well because these cash items had already had impact on cash calc
        # print(pd.DataFrame(transactions.values()))
        transactions.delete()
        return JsonResponse({'response': 'Transaction is deleted!'}, safe=False)
