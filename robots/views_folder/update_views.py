from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Model Imports
from robots.models import Robots

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