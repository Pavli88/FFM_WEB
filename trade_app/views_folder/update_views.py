from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from portfolio.models import Portfolio, Transaction
from app_functions.request_functions import *


@csrf_exempt
def close_transaction(request):
    if request.method == "POST":
        request_body = json.loads(request.body.decode('utf-8'))

        # This part changes the open status of the original trade to closed
        dynamic_model_update(table_object=Transaction,
                             request_object={'id': request_body['id'],
                                             'open_status': 'Closed'})

        # This part created the opposite cash transaction for the remaining balance
        # The price will come from the broker side
        del request_body['id']
        dynamic_model_create(table_object=Transaction(),
                             request_object=request_body)

        return JsonResponse({'response': 'Transaction is closed'}, safe=False)