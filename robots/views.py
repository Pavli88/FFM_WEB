# Django imports
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.db import connection

from mysite.processes.oanda import *
from accounts.account_functions import *
from risk.risk_functions import *
from mysite.my_functions.general_functions import *
from mysite.processes.calculations import *
from instrument.instruments_functions import *
import json

# Process imports
from robots.processes.robot_balance_calc import *
from mysite.processes.risk_calculations import *
from mysite.processes.return_calculation import *
from robots.processes.robot_pricing import pricing_robot

# Date imports
import datetime
from datetime import timedelta, datetime

# Database imports
from robots.models import *
from risk.models import *
from instrument.models import *
from accounts.models import *
from mysite.models import *
from portfolio.models import *

from trade_app.consumers import *


# CRUD -----------------------------------------------------------------------------------------------------------------



def delete_robot(request):
    print("============")
    print("DELETE ROBOT")
    print("============")
    if request.method == "POST":
        robot = request.POST.get("robot_name")
    print("ROBOT:", robot)
    print("Deleting robot from database")
    Robots.objects.filter(name=robot).delete()
    RobotRisk.objects.filter(robot=robot).delete()
    response = {"message": "Robot was deleted"}
    print("Sending data to front end")
    return JsonResponse(response, safe=False)


def get_robot_data(request):
    if request.method == "GET":
        env = request.GET.get('env')
        status = request.GET.get('status')
        robots = Robots.objects.filter(env=env).filter(status=status).values()
        print(robots)
        response = list(robots)
        return JsonResponse(response, safe=False)


def get_robots_with_instrument_data(request):
    if request.method == "GET":
        print("ROBOT WITH INSTRUMENT")
        env = request.GET.get("env")

        print("ENV", env)

        if env == "all":
            robots = Robots.objects.filter().values()
        else:
            cursor = connection.cursor()
            cursor.execute("""select rb.id, inst.id, rb.name, rb.strategy,
                                        rb.security, rb.broker, rb.status, rb.env,
                                        rb.account_number, rb.inception_date
                                from robots_robots as rb,
                                    instrument_instruments as inst
                            where inst.instrument_name=rb.name and rb.env='{env}';""".format(env=env))
            row = cursor.fetchall()

        response = list(row)

        return JsonResponse(response, safe=False)

# Revieved functions ---------------------------------------------------------------------------------------------------


@csrf_exempt
def robot_balance_calc(request):

    """
    This function calculates robot balance based on front end request.
    :param request:
    :return:
    """

    print("=========================")
    print("ROBOT BALANCE CALCULATION")
    print("=========================")
    if request.method == "POST":
        request_data = json.loads(request.body.decode('utf-8'))
        robot = request_data["robot"]
        date = datetime.datetime.strptime(request_data["start_date"], '%Y-%m-%d').date()
        end_date = datetime.datetime.strptime(request_data["end_date"], '%Y-%m-%d').date()
        print("ROBOT:", robot)
        print("START DATE:", date)
        print("END DATE:", end_date)
        if robot == "ALL":
            robot_list = Robots.objects.filter(status='active').values_list('name', flat=True)
        else:
            robot_list = [robot]
        print(robot_list)
        print("ROBOTS:", robot_list)
        for active_robot in robot_list:
            print(">>> ROBOT:", active_robot)
            start_date = date
            while start_date <= end_date:
                print("    DATE:", start_date)
                balance_calc(robot=active_robot, calc_date=start_date)
                start_date = start_date + timedelta(days=1)
    response = "Completed"
    print("Sending message to front end")
    return JsonResponse(response, safe=False)


def get_robot_balances(request, env):
    print("Robot balances")
    if request.method == "GET":
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")
    print("ENVIRONMENT:", env)
    print("START DATE:", start_date)
    print("END DATE:", end_date)
    robots = Robots.objects.filter(env=env).values_list('name', flat=True)
    response = []
    all_balance_data = pd.DataFrame(Balance.objects.filter().values())
    for robot in robots:
        robot_balance_data = all_balance_data[all_balance_data['robot_name'] == robot]
        response.append({
            'robot': robot,
            'date': robot_balance_data['date'].to_list(),
            'balance': robot_balance_data['close_balance'].to_list(),
            'cash_flow': robot_balance_data['cash_flow'].to_list(),
            'return': robot_balance_data['ret'].to_list(),
            'id': robot_balance_data['ret'].to_list()
        })
    print("Sending message to front end")
    return JsonResponse(response, safe=False)


def get_prices(request):
    if request.method == "GET":
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")
        robot = request.GET.get("robot")

        instrument = Instruments.objects.filter(instrument_name=robot).values()[0]
        print(instrument)
        prices = Prices.objects.filter(inst_code=instrument['id']).values()
        print(prices)
    return JsonResponse(list(prices), safe=False)


def get_last_price(request):
    if request.method == "GET":
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")
        robot = request.GET.get("robot")

        instrument = Instruments.objects.filter(instrument_name=robot).values()[0]

        try:
            prices = Prices.objects.filter(inst_code=instrument['id']).order_by('-id').values()[0]
        except:
            prices = {'price': 0.0, 'date': 'Missing price!'}

    return JsonResponse(prices, safe=False)


def get_robot_cf(request, robot):
    print('ROBOT CASH FLOW')
    if request.method == "GET":
        if robot == 'all':
            robot_cash_flow = RobotCashFlow.objects.filter().values()
        else:
            robot_cash_flow = RobotCashFlow.objects.filter(robot_name=robot).values()
        print(robot_cash_flow)
        return JsonResponse(list(robot_cash_flow), safe=False)


def robot_drawdown(request):
    if request.method == "GET":
        return JsonResponse(list(drawdown_calc(list(Balance.objects.filter(robot_id=request.GET.get("robot_id")).filter(
            date__gte=request.GET.get("start_date")).filter(date__lte=request.GET.get("end_date")).values_list('ret',
                                                                                                               flat=True)))),
                            safe=False)


def cumulative_return(request):
    if request.method == "GET":
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")
        robot = request.GET.get("robot")
        if robot == 'all':
            balance = Balance.objects.filter().values()
        else:
            balance = Balance.objects.filter(robot_name=robot).filter(date__gte=start_date).filter(date__lte=end_date).values_list('ret', flat=True)
        cum_rets = cumulative_return_calc(list(balance))
        return JsonResponse(list(cum_rets), safe=False)


@csrf_exempt
def robot_pricing(request):
    print("=========================")
    print("ROBOT PRICING CALCULATION")
    print("=========================")
    if request.method == "POST":
        request_data = json.loads(request.body.decode('utf-8'))
        robot = request_data["robot"]
        date = datetime.datetime.strptime(request_data["start_date"], '%Y-%m-%d').date()
        end_date = datetime.datetime.strptime(request_data["end_date"], '%Y-%m-%d').date()
        print("ROBOT:", robot)
        print("START DATE:", date)
        print("END DATE:", end_date)
        if robot == "ALL":
            robot_list = Robots.objects.filter().values_list('name', flat=True)
        else:
            robot_list = [robot]

        print("ROBOTS:", robot_list)
        response_list = []
        for active_robot in robot_list:
            instrument_id = Instruments.objects.filter(instrument_name=active_robot).values()[0]['id']
            print(">>> ROBOT:", active_robot, "INSTRUMENT ID:", instrument_id)
            start_date = date
            responses = []
            while start_date <= end_date:
                pricing_response = pricing_robot(robot=active_robot, calc_date=start_date, instrument_id=instrument_id)
                if pricing_response is None:
                    pass
                else:
                    responses.append({'date': start_date.strftime('%Y-%m-%d'),
                                      'msg': pricing_response})
                if pricing_response == "There is no calculated balance and return.":
                    break
                start_date = start_date + timedelta(days=1)
            response_list.append({'robot': active_robot, 'response': responses})
    return JsonResponse(response_list, safe=False)


def get_robot(request, robot):
    if request.method == "GET":
        robot = Robots.objects.filter(name=robot).values()
        return JsonResponse(list(robot), safe=False)


@csrf_exempt
def update_strategy_params(request):
    if request.method == "POST":
        request_data = json.loads(request.body.decode('utf-8'))
        robot = request_data["robot"]
        strategy_params = request_data["strategy_params"]
        robot = Robots.objects.get(name=robot)
        robot.strategy_params = strategy_params
        robot.save()
        print(strategy_params)
        return JsonResponse({'response': 'updated'}, safe=False)


@csrf_exempt
def update_status(request):
    if request.method == "POST":
        request_data = json.loads(request.body.decode('utf-8'))
        robot = Robots.objects.get(name=request_data["robot"])
        robot.status = request_data["status"]
        robot.save()
        return JsonResponse({'response': 'updated'}, safe=False)