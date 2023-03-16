from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Model Imports
from portfolio.models import Robots
import json


@csrf_exempt
def create_robot(request):
    request_data = json.loads(request.body.decode('utf-8'))
    if Robots.objects.filter(portfolio_code=request_data['portfolio_code'], inst_id=request_data['inst_id']).exists():
        return JsonResponse({'response': 'Security is already mapped to this portfolio'}, safe=False)
    else:
        Robots(portfolio_code=request_data['portfolio_code'],
               inst_id=request_data['inst_id'],
               ticker_id=request_data['ticker_id'],
               broker_account_id=request_data['broker_account_id']).save()
        return JsonResponse({'response': 'Security mapping is completed'}, safe=False)