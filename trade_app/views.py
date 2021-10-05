from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.http import HttpResponse

from mysite.processes.oanda import *
from mysite.models import *
from robots.models import *
from accounts.models import *
from mysite.models import *

from robots.processes.robot_balance_calc import *
from datetime import datetime

# Process imports
from trade_app.processes.trade_execution import TradeExecution


def get_open_trades_robot(request, robot):
    if request.method == "GET":
        open_trades = RobotTrades.objects.filter(robot=robot).filter(status='OPEN').values()

    return JsonResponse(list(open_trades), safe=False)


def get_open_trades(request, env):

    print("Loading open trades to open trade table")

    if request.method == "GET":
        robots = Robots.objects.filter(env=env).values_list('name', flat=True)
        trades = RobotTrades.objects.filter(status="OPEN").filter(robot__in=robots).values()

        response = list(trades)

        print("Sending data to front end")

        return JsonResponse(response, safe=False)


def new_trade(request):
    if request.method == "POST":
        request_data = json.loads(request.body.decode('utf-8'))
        robot = request.POST.get("robot")
        side = request.POST.get("side")
        trade = TradeExecution(robot=robot)
        trade.open_trade(side=side)

        response = 'Trade is opened successfully!'

        return JsonResponse(response, safe=False)


@csrf_exempt
def close_trade(request):
    print("================")
    print("MANUAL TRADE CLOSE")
    print("================")

    if request.method == "POST":
        request_data = json.loads(request.body.decode('utf-8'))
        broker_id = request_data["broker_id"]
        ffm_id = request_data["trd_id"]
        robot = request_data["robot"]

        trade = TradeExecution(robot=robot)
        trade.close_trade(ffm_id=ffm_id, broker_id=broker_id)

        response = 'Trade was closed successfully!'

        return JsonResponse(response, safe=False)


@csrf_exempt
def trade_execution(request):
    if request.method == "POST":
        message = request.body
        message = str(message.decode("utf-8"))
        signal = message.split()

        trade = TradeExecution(robot=signal[0])

        if signal[1] == 'Close':
            trade.close_all_trades()
        else:
            trade.open_trade(side=signal[1])

        return HttpResponse(None)

