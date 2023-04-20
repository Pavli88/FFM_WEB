from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from portfolio.models import Transaction
import json


@csrf_exempt
def delete_transaction(request):
    if request.method == "POST":
        request_data = json.loads(request.body.decode('utf-8'))
        Transaction.objects.filter(
            Q(id=request_data['id']) | Q(transaction_link_code=request_data['id'])).delete()
        return JsonResponse({'response': 'Transaction is deleted!'}, safe=False)
