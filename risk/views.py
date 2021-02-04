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

    print("ROBOT:", robot)
    print("DAILY RISK LIMIT:", daily_risk)
    print("DAILY MAX NUMBER OF TRADES:", nbm_trades)
    print("RISK PER TRADE:", risk_per_trade)
    print("PYRAMIDING LEVEL:", pyramiding_level)

    robot_risk_data = RobotRisk.objects.get(robot=robot)
    robot_risk_data.daily_risk_perc = daily_risk
    robot_risk_data.daily_trade_limit = nbm_trades
    robot_risk_data.risk_per_trade = risk_per_trade
    robot_risk_data.pyramiding_level = pyramiding_level
    robot_risk_data.save()

    response = {"message": "success"}

    print("Sending message to front end")

    return JsonResponse(response, safe=False)


def get_robot_risk(request):
    print("===================")
    print("GET ROBOT RISK")
    print("===================")

    robot_risk = RobotRisk.objects.filter().values()

    response = {"message": list(robot_risk)}

    print("Sending message to front end")

    return JsonResponse(response, safe=False)