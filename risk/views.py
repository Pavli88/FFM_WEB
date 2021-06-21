from django.shortcuts import render, redirect
from risk.processes.account import *
from mysite.processes.oanda import *
from mysite.views import *
from risk.models import *
from robots.views import *
from django.http import JsonResponse
from risk.forms import *


# Main site for risk management
def risk_main(request):

    """
    Loads the main page of the risk app
    :param request:
    :return:
    """

    print("==============")
    print("RISK MAIN SITE")
    print("==============")

    print("Loading all portfolios from database")

    print("Loading all robots from database")

    robots = get_robots()
    risk_form = RobotRiskForm()

    print("Loading all accounts from database")

    return render(request, 'risk_app/risk_main.html', {"robots": robots,
                                                       "risk_form": risk_form})


# URL Functions
def update_risk_per_trade(request):
    print("UPDATING RISK PER TRADE")

    if request.method == "POST":
        robot = request.POST.get("robot")
        risk_per_trade = request.POST.get("risk_per_trade")

    print("ROBOT:", robot)
    print("RISK PER TRADE:", risk_per_trade)

    robot_risk_data = RobotRisk.objects.get(robot=robot)
    robot_risk_data.risk_per_trade = risk_per_trade
    robot_risk_data.save()

    print("Risk data is updated!")

    response = {"message": "success"}

    print("Sending message to front end")

    return JsonResponse(response, safe=False)


def update_robot_risk(request):
    print("===================")
    print("UPDATING ROBOT RISK")
    print("===================")

    if request.method == "POST":
        robot = request.POST.get("robot")
        daily_risk = request.POST.get("daily_risk")
        nbm_trades = request.POST.get("daily_nmb_trades")
        risk_per_trade = request.POST.get("risk_per_trade")
        pyramiding_level = request.POST.get("pyramiding_level")
        quantity_type = request.POST.get("quantity_type")
        quantity = request.POST.get("quantity")

    print("ROBOT:", robot)
    print("DAILY RISK LIMIT:", daily_risk)
    print("DAILY MAX NUMBER OF TRADES:", nbm_trades)
    print("RISK PER TRADE:", risk_per_trade)
    print("PYRAMIDING LEVEL:", pyramiding_level)
    print("QUANTITY TYPE:", quantity_type)
    print("QUANTITY:", quantity)

    robot_risk_data = RobotRisk.objects.get(robot=robot)
    robot_risk_data.daily_risk_perc = daily_risk
    robot_risk_data.daily_trade_limit = nbm_trades
    robot_risk_data.risk_per_trade = risk_per_trade
    robot_risk_data.pyramiding_level = pyramiding_level
    robot_risk_data.quantity_type = quantity_type
    robot_risk_data.quantity = quantity
    robot_risk_data.save()

    response = {"message": "success"}

    print("Sending message to front end")

    return JsonResponse(response, safe=False)


def get_robot_risk(request, env):
    print("===================")
    print("GET ROBOT RISK")
    print("===================")
    print("ENVIRONMENT:", env)

    if request.method == "GET":
        robots = Robots.objects.filter(env=env).values_list('name', flat=True)

    print(robots)

    response = []

    all_robot_risk_data = pd.DataFrame(RobotRisk.objects.filter().values())

    for robot in robots:
        robot_risk_data = all_robot_risk_data[all_robot_risk_data['robot'] == robot]

        response.append({
            'robot': robot,
            'daily_risk': robot_risk_data['daily_risk_perc'].to_list(),
            'daily_trade_limit': robot_risk_data['daily_trade_limit'].to_list(),
            'risk_per_trade': robot_risk_data['risk_per_trade'].to_list(),
            'pyramiding_level': robot_risk_data['pyramiding_level'].to_list(),
            'quantity': robot_risk_data['quantity'].to_list(),
            'quantity_type': robot_risk_data['quantity_type'].to_list(),
            'id': robot_risk_data['id'].to_list(),
        })

    print("Sending message to front end")

    return JsonResponse(response, safe=False)