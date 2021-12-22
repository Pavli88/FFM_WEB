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
@csrf_exempt
def new_robot(request):

    """
    New robot creator function. It saves down an empty record to the robot balance table and robot risk table.
    The robot is also saved down to the instruments table.
    :param request:
    :return:
    """

    print("==================")
    print("NEW ROBOT CREATION")
    print("==================")

    if request.method == "POST":
        request_data = json.loads(request.body.decode('utf-8'))
        robot_name = request_data["robot_name"]
        strategy = request_data["strategy"]
        broker = request_data["broker"]
        env = request_data["env"]
        security = request_data["security"]
        account_number = request_data["account"]

        print("ROBOT NAME:", robot_name)
        print("STRATEGY:", strategy)
        print("BROKER:", broker)
        print("ENVIRONMENT:", env)
        print("SECURITY:", security)
        print("ACCOUNT:", account_number)

        try:
            Robots(name=robot_name,
                   strategy=strategy,
                   security=security,
                   broker=broker,
                   status="active",
                   env=env,
                   account_number=account_number
                   ).save()

            print("Inserting new robot to database")

            Balance(robot_name=robot_name).save()

            print("Setting up initial balance to 0")

            Instruments(instrument_name=robot_name,
                        instrument_type="Robot",
                        source="ffm_system").save()

            print("Saving new robot to instruments table")

            print("Creating new record in robot risk table")

            RobotRisk(robot=robot_name).save()

            print("Saving down robot to instruments table")

            response = {"securities": []}

        except:
            print("Robot exists in database")
            response = {"message": "alert"}

    SystemMessages(msg_type="NEW ROBOT",
                   msg=robot_name + ": New robot was created.").save()

    print("Sending response to front end")
    print("")

    return JsonResponse(response, safe=False)


@csrf_exempt
def update_robot(request):
    if request.method == "POST":
        request_data = json.loads(request.body.decode('utf-8'))
        robot = Robots.objects.get(name=request_data['name'])

        for key, value in request_data.items():
            setattr(robot, key, value)

        robot.save()

        return JsonResponse(list({}), safe=False)


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


def get_robots(request, env):

    print("Request from front end to load all robot data")

    if request.method == "GET":

        if env == "all":
            robots = Robots.objects.filter().values()
        else:
            robots = Robots.objects.filter(env=env).values()

        response = list(robots)

        print("Sending data to front end")
        print("")

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
            robot_list = Robots.objects.filter().values_list('name', flat=True)
        else:
            robot_list = [robot]

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


def get_robot_balance(request):
    print("single robot balance")

    if request.method == "GET":
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")
        robot = request.GET.get("robot")

        print("ROBOT:", robot)
        print("START DATE:", start_date)
        print("END DATE:", end_date)

        balance = Balance.objects.filter(robot_name=robot).filter(date__gte=start_date).values()

        return JsonResponse(list(balance), safe=False)


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
    if request.method == "GET":

        if robot == 'all':
            robot_cash_flow = RobotCashFlow.objects.filter().values()
        else:
            robot_cash_flow = RobotCashFlow.objects.filter(robot_name=robot).values()

        return JsonResponse(list(robot_cash_flow), safe=False)


def robot_drawdown(request):

    print("Drawdown calculation")

    if request.method == "GET":

        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")
        robot = request.GET.get("robot")

        if robot == 'all':
            balance = Balance.objects.filter().values()
        else:
            balance = Balance.objects.filter(robot_name=robot).filter(date__gte=start_date).filter(date__lte=end_date).values_list('ret', flat=True)

        drawdown = drawdown_calc(list(balance))

        return JsonResponse(list(drawdown), safe=False)


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
    """
        This function calculates robot balance based on front end request.
        :param request:
        :return:
        """

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


def get_trades(request):
    if request.method == "GET":
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")
        robot = request.GET.get("robot")

        if robot == 'all':
            trades = RobotTrades.objects.filter().values()
        else:
            trades = RobotTrades.objects.filter(robot=robot).filter(close_time__gte=start_date).filter(close_time__lte=end_date).values()

        return JsonResponse(list(trades), safe=False)


def get_robot(request, robot):
    if request.method == "GET":
        print(robot)
        robot = Robots.objects.filter(name=robot).values()
        print(robot)
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


