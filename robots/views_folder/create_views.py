from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Model Imports
from robots.models import Strategy

import json


@csrf_exempt
def create_robot_strategy(request):
    if request.method == "POST":
        request_data = json.loads(request.body.decode('utf-8'))
        try:
            Strategy(name=request_data["name"], description=request_data["description"]).save()
            return JsonResponse({'response': 'Strategy inserted into database'}, safe=False)
        except:
            return JsonResponse({'response': 'Strategy already exists in database'}, safe=False)
