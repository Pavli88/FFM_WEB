from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Model imports
from robots.models import RobotTrades

# Package Imports
import json


@csrf_exempt
def delete_transaction(request):
    if request.method == 'POST':
        request_data = json.loads(request.body.decode('utf-8'))
        RobotTrades.objects.get(id=request_data['id']).delete()
        return JsonResponse('Transaction is deleted', safe=False)