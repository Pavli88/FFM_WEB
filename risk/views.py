from django.shortcuts import render, redirect
from risk.processes.account import *
from mysite.processes.oanda import *
from mysite.views import *
from risk.models import *
from robots.views import *
from django.http import JsonResponse


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

    print("Loading all accounts from database")

    return render(request, 'risk_app/risk_main.html', {"robots": robots})


def update_robot_risk(request):
    print("===================")
    print("UPDATING ROBOT RISK")
    print("===================")

    if request.method == "POST":
        robot = request.POST.get("robot")
        daily_risk = request.POST.get("daily_risk")

    print("ROBOT:", robot)
    print("DAILY RISK LIMIT:", daily_risk)

    robot_risk_data = RobotRisk.objects.get(robot=robot)
    robot_risk_data.daily_risk_perc = daily_risk
    robot_risk_data.save()

    response = {"message": "success"}

    print("Sending message to front end")

    return JsonResponse(response, safe=False)


def get_robot_risk(request):
    print("===================")
    print("GET ROBOT RISK")
    print("===================")

    if request.method == "GET":
        robot = request.GET.get("robot")

    print("ROBOT:", robot)

    robot_risk = RobotRisk.objects.filter(robot=robot).values()

    response = {"message": list(robot_risk)}

    print("Sending message to front end")

    return JsonResponse(response, safe=False)