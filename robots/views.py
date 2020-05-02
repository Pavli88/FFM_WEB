from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from robots.models import *
import os


# Main site for robot configuration
def robots_main(request):

    robots = Robots.objects.filter().values('name')
    robot_list = []
    for robot in robots:
        robot_list.append(robot["name"])

    print("Robot list:", robot_list)
    return render(request, 'robots_app/create_robot.html', {"robot_list": robot_list})


# Trade execution based on Tradingviw feed
@csrf_exempt
def execute_trade(request):

    """
    This function executes trade signals coming from Tradingview.com
    :param request:
    :return:
    """

    if request.method == "POST":

        message = request.body
        print(message.decode("utf-8"))

        env = "practice"
        quantity = 1000
        start_bal = 100000
        sec = "EUR_USD"
        risk_perc = 0.01
        pl = 4
        sl_prec = 4

        if (message.decode("utf-8")) == "BUY":
            os.system('/home/pavliati/python3/project/bin/python /home/pavliati/mysite/codes/python/execute.py --env {env} --st_bal {start_bal} --sec {sec} --q {quantity} --sl perc --slpv {risk_perc} --pl {pl} --sl_prec {sl_prec}'.format(quantity=quantity, start_bal=start_bal, sec=sec, risk_perc=risk_perc, pl=pl, env=env, sl_prec=sl_prec))
            return HttpResponse(None)
        elif (message.decode("utf-8")) == "SELL":
            os.system('/home/pavliati/python3/project/bin/python /home/pavliati/mysite/codes/python/execute.py --env {env} --st_bal {start_bal} --sec {sec} --q -{quantity} --sl perc --slpv {risk_perc} --pl {pl} --sl_prec {sl_prec}'.format(quantity=quantity, start_bal=start_bal, sec=sec, risk_perc=risk_perc, pl=pl, env=env, sl_prec=sl_prec))
            return HttpResponse(None)
        elif (message.decode("utf-8")) == "CLOSE":
            os.system('/home/pavliati/python3/project/bin/python /home/pavliati/mysite/codes/python/close_positions.py --ca all --env live')
            return HttpResponse(None)

    if request.method == "GET":
        print("Trade execution")
        return HttpResponse("This site is for trade execution")


def create_robot(request):

    """
    This function creates new robot entry in the data base
    :param request:
    :return:
    """

    if request.method == "POST":

        print("New robot creation request received.")

        # String fields
        robot_name = request.POST.get("robot_name")
        strategy_name = request.POST.get("strategy_name")
        security = request.POST.get("security")
        broker = request.POST.get("broker")
        status = request.POST.get("status")
        env = request.POST.get("env")
        time_frame = request.POST.get("time_frame")
        account_number = request.POST.get("account_number")
        sl_policy = request.POST.get("sl_policy")

        string_parameter_dict = {"robot name": robot_name,
                                 "strategy name": strategy_name,
                                 "security": security,
                                 "broker": broker,
                                 "status": status,
                                 "environment": env,
                                 "time_fame:": time_frame,
                                 "account_number": account_number,
                                 "sl_policy": sl_policy}

        # Float fields
        pyramiding_level = float(request.POST.get("pyramiding_level"))
        init_exp = float(request.POST.get("init_exp"))
        quantity = float(request.POST.get("quantity"))

        print("Robot parameters:", string_parameter_dict)

        # Checking if robot name exists in data base
        print("Checking if new record exists in database")
        try:
            data_exists = Robots.objects.get(name=robot_name).name
        except:
            data_exists = "does not exist"

        if data_exists == robot_name:
            print("Robot exists in data base.")
            return render(request, 'robots_app/create_robot.html', {"exist_robots": "exists"})

        # Inserting new robot data to database
        print("Inserting new record to database")
        robot = Robots(name=robot_name,
                       strategy=strategy_name,
                       security=security,
                       broker=broker,
                       status=status,
                       pyramiding_level=pyramiding_level,
                       in_exp=init_exp,
                       env=env,
                       quantity=quantity,
                       time_frame=time_frame,
                       account_number=account_number,
                       sl_policy=sl_policy)

        try:
            robot.save()
            print("New record was created with parameters:", string_parameter_dict)
            return render(request, 'robots_app/create_robot.html', {"exist_robots": "created"})
        except:
            print("Error occured while inserting data to database. "
                  "Either data type or server configuration is not correct.")
            return render(request, 'robots_app/create_robot.html',
                          {"exist_robots": "Incorrect data type was given in one of the fields!"})


def get_all_robots(request):

    """
    Queries out all robots from database and passes it back to the html
    :param request:
    :return:
    """
    robots = Robots.objects.filter().values()

    header_list = []
    for header in robots[0]:
        header_list.append(header)

    # Create code to give the data back in json
    return render(request, 'robots_app/create_robot.html', {"robots": robots})


def amend_robot(request):

    if request.method == "POST":
        # String fields
        robot_name = request.POST.get("robot_name")
        print(robot_name)


