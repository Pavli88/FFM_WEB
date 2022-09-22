from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Model Imports
from robots.models import Balance, MonthlyReturns

# Package Imports
import pandas as pd
import json

# Process Imports
from robots.processes.performance import monthly_return_calc


@csrf_exempt
def monthly_return(request):
    if request.method == 'POST':
        request_data = json.loads(request.body.decode('utf-8'))
        print(request_data['month'])
        month_end_date = request_data['year'] + '-' + request_data['month']
        start_date = month_end_date[0:8] + '01'
        print(start_date)
        response = []
        for robot in request_data['robot']:
            print(robot)
            msg = monthly_return_calc(robot_code=robot, start_date=start_date, end_date=month_end_date)
            response.append(month_end_date + ': ' + msg)
        return JsonResponse(response, safe=False)