from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Model Imports
from robots.models import Strategy, Robots, Balance, RobotCashFlow
from risk.models import RobotRisk

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


@csrf_exempt
def create_robot(request):
    if request.method == "POST":
        request_data = json.loads(request.body.decode('utf-8'))
        try:
            new_robot = Robots(name=request_data["robot_name"],
                               status="inactive",
                               env=request_data["env"],
                               currency=request_data['currency'],
                               inception_date=request_data["inception_date"])
            new_robot.save()
            print(new_robot.id)
        except:
            response = 'Robot name exists in database'
            return JsonResponse(response, safe=False)
        Balance(robot_id=new_robot.id).save()
        # Instruments(instrument_name=request_data["robot_name"],
        #             inst_code=request_data["robot_code"],
        #             instrument_type="Robot",
        #             source="ffm_system").save()
        RobotCashFlow(robot_name=new_robot.id,
                      cash_flow=0.0,
                      date=request_data["inception_date"]).save()
        RobotRisk(robot=new_robot.id).save()
        return JsonResponse('New robot created in database', safe=False)
