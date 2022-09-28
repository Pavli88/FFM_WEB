from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Model Imports
from robots.models import Balance, MonthlyReturns, Robots

# Package Imports
import pandas as pd
import json

# Date imports
import datetime
from datetime import timedelta, datetime

# Process Imports
from robots.processes.performance import monthly_return_calc
from robots.processes.robot_balance_calc import *


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
            msg = monthly_return_calc(robot_id=robot, start_date=start_date, end_date=month_end_date)
            response.append(month_end_date + ': ' + msg)
        return JsonResponse(response, safe=False)


@csrf_exempt
def robot_balance(request):
    if request.method == "POST":
        request_data = json.loads(request.body.decode('utf-8'))
        robot = request_data["robot_id"]
        date = datetime.datetime.strptime(request_data["start_date"], '%Y-%m-%d').date()
        end_date = datetime.datetime.strptime(request_data["end_date"], '%Y-%m-%d').date()
        if robot == "ALL":
            robot_list = Robots.objects.filter(status='active').values_list('id', flat=True)
        else:
            robot_list = [robot]
        print("ROBOTS:", robot_list)
        for active_robot in robot_list:
            print(">>> ROBOT:", active_robot)
            start_date = date
            while start_date <= end_date:
                print("    DATE:", start_date)
                balance_calc(robot_id=active_robot, calc_date=start_date)
                start_date = start_date + timedelta(days=1)
    response = "Completed"
    return JsonResponse(response, safe=False)