from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from mysite.models import *
import pandas as pd
from datetime import date
import datetime
from robots.models import *
from accounts.models import *
from mysite.processes.oanda import *


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


def get_balance_history(start_date, end_date):

    print("")
    print("RETREIVING BALANCE HISTORY FROM BROKER")

    default_account = HomePageDefault.objects.filter().values()
    print("Account Number:", default_account[0]["account_number"])
    account = BrokerAccounts.objects.filter(account_number=default_account[0]["account_number"]).values()

    print("Token:", account[0]["access_token"])

    if account[0]["env"] == "demo":
        env = "practice"
    else:
        env = "live"

    print("Environment:", env)

    oanda = Oanda(environment=env,
                  acces_token=account[0]["access_token"],
                  account_number=default_account[0]["account_number"])

    transactions = oanda.get_transactions(start_date=start_date, end_date=end_date)
    balance = list(transactions[["accountBalance"]].dropna()["accountBalance"].astype(float))
    balance_label = [bal for bal in range(len(balance))]

    print("")

    return balance, balance_label


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


def get_account_data():

    """
    Function to get all account data
    :return:
    """

    accounts = BrokerAccounts.objects.filter().values()

    return accounts


def get_open_trades():

    """
    Function to get open trades
    :return:
    """

    open_trades = Trades.objects.filter(status="OPEN").values()

    return open_trades


def get_robot_list(account=None):

    """
    Function to get a list of robots from the db.
    :return:
    """

    if account is None:
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
                                         "accounts": get_account_data(),
                                         "pnl_label": [],
                                         "pnls": [],
                                         "cum_pnl": [],
                                         "balance": [],
                                         "balance_label": [],
                                         })


def save_layout(request):

    print("Saving home page layout")

    if request.method == "POST":
        account = request.POST.get("account")

    HomePageDefault(account_number=account).save()

    print("Account:", account)

    return render(request, 'home.html', {"beg_month": get_beg_month(),
                                         "today": get_today(),
                                         "robots": get_robot_list(),
                                         "open_trades": get_open_trades(),
                                         "accounts": get_account_data(),
                                         "pnl_label": [],
                                         "pnls": [],
                                         "cum_pnl": [],
                                         "balance": [],
                                         "balance_label": [],
                                         })


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

    # Loading account balance from broker
    print("Get account history from broker")
    balance_list = get_balance_history(start_date=start_date, end_date=end_date)

    # If there is no record for the robot for the preiod the codes goes to this line
    if all_pnls == "empty":

        print("Empty Dataframe")
        return render(request, 'home.html', {"today": get_today(),
                                             "beg_month": get_beg_month(),
                                             "robots": get_robot_list(),
                                             "message": "empty",
                                             "accounts": get_account_data(),
                                             "balance": balance_list[0],
                                             "balance_label": balance_list[1],
                                             "pnl_label": [],
                                             "pnls": [],
                                             "cum_pnl": [],
                                             })

    return render(request, 'home.html', {"pnls": all_pnls[1],
                                         "pnl_label": all_pnls[0],
                                         "cum_pnl": all_pnls[2],
                                         "today": get_today(),
                                         "beg_month": get_beg_month(),
                                         "robots": get_robot_list(),
                                         "accounts": get_account_data(),
                                         "balance": balance_list[0],
                                         "balance_label": balance_list[1],
                                         "message": "",
                                         })


# Settings
def go_to_settings(request):

    print("Load settings")

    try:
        settings = Settings.objects.filter(id=1).values()
        st_time = settings[0]["ov_st_time"].strftime("%H:%M")
        en_time = settings[0]["ov_en_time"].strftime("%H:%M")
        print(settings[0])
        print(st_time)
    except:
        return render(request, 'settings.html')

    return render(request, 'settings.html', {"st_time": st_time,
                                             "en_time": en_time})


def save_settings(request):

    if request.method == "POST":
        switch = request.POST.get("switch")
        st_time = request.POST.get("st_time")
        en_time = request.POST.get("en_time")

    print("Amending settings")
    print("")
    print("Overnight trading:", switch)
    print("Start Time:", st_time)
    print("End Time:", en_time)

    print("Saving settings to data base")

    if switch == "on":
        ov_status = True
    else:
        ov_status = False

    try:
        print("Amending existing settings in database")
        settings = Settings.objects.get(id=1)
        settings.ov_status = ov_status
        settings.ov_st_time = st_time
        settings.ov_en_time = en_time
        settings.save()
        print("Settings has been amended")

    except:
        print("Settings is empty first record is being created")

        print("Saving first record to database")
        settings = Settings(ov_status=ov_status,
                            ov_st_time=st_time,
                            ov_en_time=en_time)

        settings.save()
        print("Record has been saved")

    return redirect('settings main')












