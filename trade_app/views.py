from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from mysite.processes.oanda import *
from mysite.models import *
from robots.models import *
from accounts.models import *
from mysite.models import *

from robots.processes.robot_balance_calc import *
from datetime import datetime


def get_open_trades(request, env):

    print("Loading open trades to open trade table")

    if request.method == "GET":
        robots = Robots.objects.filter(env=env).values_list('name', flat=True)
        trades = RobotTrades.objects.filter(status="OPEN").filter(robot__in=robots).values()

        response = list(trades)

        print("Sending data to front end")

        return JsonResponse(response, safe=False)


@csrf_exempt
def close_trade(request):
    print("================")
    print("MANUAL TRADE CLOSE")
    print("================")

    if request.method == "POST":
        request_data = json.loads(request.body.decode('utf-8'))
        broker_id = request_data["broker_id"]
        robot = request_data["robot"]
        trd_id = request_data["trd_id"]

        print("BROKER ID", broker_id)
        print("ROBOT", robot)
        print("ID", trd_id)

        robot_data = Robots.objects.filter(name=robot).values()
        account_data = BrokerAccounts.objects.filter(account_number=robot_data[0]["account_number"]).values()
        environment = robot_data[0]["env"]

        if environment == "live":
            env = "live"
        else:
            env = "practice"

        print("Closing Trade")

        try:
            open_trade = OandaV20(access_token=account_data[0]["access_token"],
                                  account_id=account_data[0]["account_number"],
                                  environment=env).close_trades(trd_id=broker_id)
        except:
            print('Trade does is not open at broker s side!')
            response = 'Trade does is not open at broker s side!'
            return JsonResponse(response, safe=False)

        print("Update -> Database ID:", trd_id)

        trade_record = RobotTrades.objects.get(id=trd_id)
        trade_record.status = "CLOSED"
        trade_record.close_price = open_trade["price"]
        trade_record.pnl = open_trade["pl"]
        trade_record.close_time = datetime.today().date()
        trade_record.save()

        print("Calculating balance for robot")

        balance_calc_msg = balance_calc(robot=robot, calc_date=str(datetime.today().date()))

        print(balance_calc_msg)

        print("Sending message to system messages table")

        SystemMessages(msg_type="TRADE EXECUTION",
                       msg=robot + ": Closing trade manually").save()

        response = 'Trade was closed successfully!'

        return JsonResponse(response, safe=False)


def submit_trade(request):
    print("================")
    print("NEW MANUAL TRADE")
    print("================")

    if request.method == "POST":
        request_data = json.loads(request.body.decode('utf-8'))
        robot = request.POST.get("robot")
        quantity = request.POST.get("quantity")
        sl = request.POST.get("sl")

    print("ROBOT:", robot)
    print("QUANTITY:", quantity)

    if float(quantity) > 0:
        trade_side = "BUY"
    elif float(quantity) < 0:
        trade_side = "SELL"

    robot_data = Robots.objects.filter(name=robot).values()
    account_data = BrokerAccounts.objects.filter(account_number=robot_data[0]["account_number"]).values()
    account_number = account_data[0]["account_number"]
    token = account_data[0]["access_token"]
    environment = account_data[0]["env"]
    security = robot_data[0]["security"]

    if environment == "live":
        env = "live"
    else:
        env = "practice"

    print("ACCOUNT NUMBER:", account_number)
    print("TOKEN", token)
    print("ENVIRONMENT:", environment)
    print("SECURITY", security)
    print("Connecting to Broker API")

    trade = OandaV20(access_token=token,
                     account_id=account_number,
                     environment=env).submit_market_order(security=security, quantity=quantity, sl_price=sl)

    print("Order was submitted to broker successfully!")

    print("Saving open trades data to FFM SYSTEM")

    RobotTrades(security=security,
                robot=robot,
                quantity=quantity,
                status="OPEN",
                pnl=0.0,
                open_price=trade["price"],
                side=trade_side,
                broker_id=trade["id"],
                broker="oanda").save()

    print("Robot trade table is updated!")

    print("Sending message to system messages table")

    SystemMessages(msg_type="TRADE EXECUTION",
                   msg="Trade executed for " + robot + "@" + quantity).save()

    return redirect('trade_app main')
