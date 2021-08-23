# Django imports
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

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
from robots.processes.robot_pricing import *

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


def amend_robot(request):

    if request.method == "POST":

        """
        Function to amend existing robot data in the database.
        """
        message = request.body
        message = str(message.decode("utf-8"))

        # Gets data from html table
        robot_name = request.POST.get("robot_name")
        env = request.POST.get("env")
        status = request.POST.get("status")
        pyramiding_level = request.POST.get("pyramiding_level")
        init_exp = request.POST.get("init_exp")
        quantity = request.POST.get("quantity")
        account_number = request.POST.get("account_number")
        precision = request.POST.get("precision")

        print("Request received to amend robot record for", robot_name)
        print("New Robot Parameters:")
        print("Robot Name:", robot_name)
        print("Environment:", env)
        print("Status:", status)
        print("P Level:", pyramiding_level)
        print("Initial Exp:", init_exp)
        print("Quantity:", quantity)
        print("Account Number:", account_number)
        print("Precision:", precision)

        # Retrieves back amended robot info and refreshes table
        robot = Robots.objects.get(name=robot_name)
        robot.quantity = quantity
        robot.env = env
        robot.status = status
        robot.pyramiding_level = pyramiding_level
        robot.init_exp = init_exp
        robot.quantity = quantity
        robot.account_number = account_number
        robot.prec = precision
        robot.save()
        print("Amended parameters were saved to database.")

        return render(request, 'robots_app/create_robot.html', {"robots": Robots.objects.filter().values()})


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

        balance = Balance.objects.filter(robot_name=robot).values()

        return JsonResponse(list(balance), safe=False)


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

        for active_robot in robot_list:
            print(">>> ROBOT:", active_robot)

            start_date = date

            while start_date <= end_date:
                print("    DATE:", start_date)
                pricing(robot=active_robot, calc_date=start_date)
                start_date = start_date + timedelta(days=1)

    response = "Completed"

    print("Sending message to front end")

    return JsonResponse(response, safe=False)


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



