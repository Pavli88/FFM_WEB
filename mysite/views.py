from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from mysite.models import *
import pandas as pd
from datetime import date
import datetime
from robots.models import *


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

    trade_df = pd.DataFrame(list(trades))

    if trade_df.empty is True:
        print("Empty Dataframe")
        return render(request, 'home.html', {"today": get_today(),
                                             "beg_month": get_beg_month(),
                                             "robots": get_robot_list(),
                                             "message": "Record does not exists"})

    open_prices = list(trade_df["open_price"])
    close_prices = list(trade_df["close_price"])
    units = list(trade_df["quantity"])
    actions = list(trade_df["side"])

    pnls = []

    for open, close, unit, action in zip(open_prices, close_prices, units, actions):
        print(open, close, unit, action)
        if action == "BUY":
            pnl = (open-close)*unit
            pnls.append(pnl)
        elif action == "SELL":
            pnl = ((open-close)*unit)*-1
            pnls.append(pnl)

    pnl_label = [label for label in range(len(pnls))]
    cum_pnl = cumulative(pnls)

    print(pnl_label)
    print("PNLs:", pnls)
    print("Cum PNL:", cum_pnl)

    return render(request, 'home.html', {"pnls": pnls,
                                         "pnl_label": pnl_label,
                                         "cum_pnl": cum_pnl,
                                         "today": get_today(),
                                         "beg_month": get_beg_month(),
                                         "robots": get_robot_list(),
                                         "message": ""})













