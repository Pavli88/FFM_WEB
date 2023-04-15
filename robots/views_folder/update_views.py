from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Model Imports
from robots.models import Robots, Strategy

# Package Imports
import json


@csrf_exempt
def update_robot(request):
    if request.method == "POST":
        request_data = json.loads(request.body.decode('utf-8'))
        robot = Robots.objects.get(id=request_data['robot_id'])
        for key, value in request_data.items():
            setattr(robot, key, value)
        robot.save()
        return JsonResponse('Robot details are updated', safe=False)


@csrf_exempt
def update_robot_strategy(request):
    if request.method == "POST":
        request_data = json.loads(request.body.decode('utf-8'))
        try:
            strategy = Strategy.objects.get(id=request_data['id'])
            for key, value in request_data.items():
                setattr(strategy, key, value)
            strategy.save()
            return JsonResponse({'response': 'Robot strategy is updated'}, safe=False)
        except Strategy.DoesNotExist:
            return JsonResponse({'response': 'Robot strategy does not exists in database'}, safe=False)
        except:
            return JsonResponse({'response': 'Robot strategy exists in database'}, safe=False)