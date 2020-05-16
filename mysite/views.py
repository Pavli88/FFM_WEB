from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from mysite.models import *
import pandas as pd
from datetime import date
import datetime
from robots.models import *


def pnl_generator(trades):

    trade_df = pd.DataFrame(list(trades))

    if trade_df.empty is True:
        return "empty"

    open_prices = list(trade_df["open_price"])
    close_prices = list(trade_df["close_price"])
    units = list(trade_df["quantity"])
    actions = list(trade_df["side"])

    pnls = []

    for open, close, unit, action in zip(open_prices, close_prices, units, actions):

        if action == "BUY":
            pnl = (close-open)*unit
            pnls.append(pnl)
        elif action == "SELL":
            pnl = ((close-open)*unit)*-1
            pnls.append(pnl)

    pnl_label = [label for label in range(len(pnls))]
    cum_pnl = cumulative(pnls)

    print(pnl_label)
    print("PNLs:", pnls)
    print("Cum PNL:", cum_pnl)

    return pnl_label, pnls, cum_pnl

# Python code to get the Cumulative sum of a list
def cumulative(lists):

    """
    Function that creates cumulative list based on given list
    :param lists:
    :return:
    """

    cu_list = []
    length = len(lists)
    cu_list = [sum(lists[0:x:1]) for x in range(0, length+1)]
    return cu_list[1:]


def get_today():

    """
    This function gets today's value and returns it back as a string
    :return:
    """

    today = date.today()
    return str(today)


def get_beg_month():

    """
    Function to get the first day of the month as date
    :return:
    """

    today = date.today()
    datem = datetime.datetime(today.year, today.month, 1)

    return str(datem)[0:10]


def get_open_trades():

    open_trades = Trades.objects.filter(status="OPEN").values()

    return open_trades


def get_robot_list():

    """
    Function to get a list of robots from the db.
    :return:
    """

    robots = Robots.objects.filter().values()
    robot_df = pd.DataFrame(list(robots))
    robot_list = list(robot_df["name"])
    robot_list.append("ALL")

    return robot_list


# Home page
def home(request):

    print("Loading robot list from db:", get_robot_list())

    return render(request, 'home.html', {"beg_month": get_beg_month(),
                                         "today": get_today(),
                                         "robots": get_robot_list(),
                                         "open_trades": get_open_trades(),
                                         "message": ""})


def get_results(request):

    if request.method == "POST":
        trade_side = request.POST.get("side")
        robot_name = request.POST.get("robot_name")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")

        print("Parameters received:")
        print("Trade Side:", trade_side)
        print("Robot Name:", robot_name)
        print("Start Date: ", start_date)

    print("Today's date:", get_today())

    if trade_side == "ALL" and robot_name == "ALL":
        trades = Trades.objects.filter(status="CLOSE",
                                       close_time__range=[start_date, end_date]).values()
    elif robot_name == "ALL":
        trades = Trades.objects.filter(status="CLOSE",
                                       side=trade_side,
                                       close_time__range=[start_date, end_date]).values()
    else:
        print("Robot+Side parameters")
        trades = Trades.objects.filter(status="CLOSE",
                                       side=trade_side,
                                       robot=robot_name,
                                       close_time__range=[start_date, end_date]).values()

    all_trades = Trades.objects.filter(status="CLOSE",
                                       close_time__range=[start_date, end_date]).values()

    all_pnls = pnl_generator(trades=trades)

    # If there is no record for the robot for the preiod the codes goes to this line
    if all_pnls == "empty":
        print("Empty Dataframe")
        return render(request, 'home.html', {"today": get_today(),
                                             "beg_month": get_beg_month(),
                                             "robots": get_robot_list(),
                                             "message": "Record does not exists"})

    return render(request, 'home.html', {"pnls": all_pnls[1],
                                         "pnl_label": all_pnls[0],
                                         "cum_pnl": all_pnls[2],
                                         "today": get_today(),
                                         "beg_month": get_beg_month(),
                                         "robots": get_robot_list(),
                                         "message": "",
                                         })













