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
    transactions = transactions[transactions["reason"] == "MARKET_ORDER_TRADE_CLOSE"]

    balance = list(transactions[["accountBalance"]].dropna()["accountBalance"].astype(float))
    balance_label = [bal for bal in range(len(balance))]

    trades = list(transactions["pl"])

    trades_label = [trd for trd in range(len(trades))]

    total_pnl = round(sum([float(i) for i in trades]), 2)
    trade_return = round((total_pnl / float(balance[0]))*100, 2)

    trade_colors = []

    for trade in trades:
        if float(trade) < 0:
            trade_colors.append('#842518')
        else:
            trade_colors.append('#405347')

    number_of_trades = len(balance)

    print("")

    balance_dict = {"balance": balance,
                    "label": balance_label}

    trades_dict = {"trades": trades,
                   "label": trades_label,
                   "colors": trade_colors,
                   "total_pnl": total_pnl,
                   "return": trade_return}

    return balance, balance_label, number_of_trades, trades_dict


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


def get_days():

    """
    This function gets today's value and returns it back as a string
    :return:
    """

    today = date.today()
    t_plus_one = today + datetime.timedelta(days=1)
    datem = datetime.datetime(today.year, today.month, 1)

    dates = {"today": str(today),
             "next_day": str(t_plus_one),
             "beg_month": str(datem)}

    return dates


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


def calculate_risk_exposure():

    """
    This function calculates SL exposure and gives back the list of these ammounts
    :return:
    """

    open_trades = pd.DataFrame(list(get_open_trades()))
    sl_list = list(open_trades["sl"])
    open_price_list = list(open_trades["open_price"])
    side_list = list(open_trades["side"])
    quantity_list = list(open_trades["quantity"])

    risk_list = []

    for sl, price, side, qt in zip(sl_list, open_price_list, side_list, quantity_list):
        if side == "SELL":
            risk = (sl - price)*-1*qt
        else:
            risk = (sl - price) * qt

        risk_list.append(round(risk, 2))

    print(sum(risk_list))
    risk_dict = {"sum_risk": sum(risk_list),
                 "risk_list": risk_list}

    return risk_dict


def get_robot_list(account=None):

    """
    Function to get a list of robots from the db.
    :return:
    """

    if account is None:
        robots = Robots.objects.filter().values()
    else:
        robots = Robots.objects.filter(account_number=account).values()

    robot_df = pd.DataFrame(list(robots))
    robot_list = list(robot_df["name"])
    robot_list.append("ALL")

    return robot_list


# Home page
def home(request):

    print("")
    print("Loading default settings")

    default_data = HomePageDefault.objects.filter().values()
    default_account = default_data[0]["account_number"]
    robot_list = get_robot_list(account=default_account)
    print("Default Account:", default_account)
    print("Loading robot list from db:", robot_list)

    return render(request, 'home.html', {"dates": get_days(),
                                         "robots": robot_list,
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

    return render(request, 'home.html', {"dates": get_days(),
                                         "robots": get_robot_list(),
                                         "open_trades": get_open_trades(),
                                         "accounts": get_account_data(),
                                         "pnl_label": [],
                                         "pnls": [],
                                         "cum_pnl": [],
                                         "balance": [],
                                         "balance_label": [],
                                         })


def get_trade_pnls(trades):

    trade_df = pd.DataFrame(list(trades))
    print(trade_df)

    color_list = []

    if trade_df.empty is True:
        return "empty"

    for side in list(trade_df["side"]):
        if side == "SELL":
            color_list.append('#842518')
        elif side == "BUY":
            color_list.append('#405347')

    robots = get_robot_list()

    robot_pnl_list = []
    robot_color_list = []

    for robot in robots:
        robot_df = trade_df[trade_df["robot"] == robot]
        robot_pnl = round(robot_df["pnl"].sum(), 2)
        robot_pnl_list.append(robot_pnl)

        if float(robot_pnl) < 0:
            robot_color_list.append('#842518')
        else:
            robot_color_list.append('#405347')

    print(robot_pnl_list)

    pnls = list(trade_df["pnl"])
    pnl_label = [label for label in range(len(pnls))]
    cum_pnl = cumulative(pnls)

    pnl_dict = {"pnls": pnls,
                "labels": pnl_label,
                "cum_pnl": cum_pnl,
                "colors": color_list,
                "number_of_trades": len(pnls)}

    robot_pnls = {"robot_pnl": robot_pnl_list,
                  "robot_label": robots,
                  "color": robot_color_list}

    return pnl_dict, robot_pnls


def get_results(request):

    print("")
    print("Loading default settings")

    default_data = HomePageDefault.objects.filter().values()
    default_account = default_data[0]["account_number"]
    robot_list = get_robot_list(account=default_account)
    print("Default Account:", default_account)
    print("Loading robot list from db:", robot_list)

    if request.method == "POST":
        trade_side = request.POST.get("side")
        robot_name = request.POST.get("robot_name")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")

        print("Parameters received:")
        print("Trade Side:", trade_side)
        print("Robot Name:", robot_name)
        print("Start Date: ", start_date)

    print("Today's date:", get_days()["today"])

    if trade_side == "ALL" and robot_name == "ALL":
        trades = Trades.objects.filter(status="CLOSE",
                                       close_time__range=[start_date, end_date]).values()
    elif trade_side == "ALL":
        trades = Trades.objects.filter(status="CLOSE",
                                       robot=robot_name,
                                       close_time__range=[start_date, end_date]).values()
    else:
        print("Robot+Side parameters")
        trades = Trades.objects.filter(status="CLOSE",
                                       side=trade_side,
                                       robot=robot_name,
                                       close_time__range=[start_date, end_date]).values()

    all_pnls = get_trade_pnls(trades=trades)

    # Loading account balance from broker
    print("Get account history from broker")
    balance_list = get_balance_history(start_date=start_date, end_date=end_date)

    # SL Exposure
    sl_exposure_list = calculate_risk_exposure()

    # If there is no record for the robot for the preiod the codes goes to this line
    if all_pnls == "empty":

        print("Empty Dataframe")
        return render(request, 'home.html', {"dates": get_days(),
                                             "robots": robot_list,
                                             "message": "empty",
                                             "accounts": get_account_data(),
                                             "balance": balance_list[0],
                                             "balance_label": balance_list[1],
                                             "nmbr_trades_bal": balance_list[2],
                                             "robot_perf": [],
                                             "pnl": [],

                                             })

    return render(request, 'home.html', {"dates": get_days(),
                                         "robots": robot_list,
                                         "robot_name": robot_name,
                                         "accounts": get_account_data(),
                                         "balance": balance_list[0],
                                         "balance_label": balance_list[1],
                                         "nmbr_trades_bal": balance_list[2],
                                         "side": trade_side,
                                         "robot_perf": all_pnls[1],
                                         "pnl": all_pnls[0],
                                         "br_trades": balance_list[3],
                                         "risk": sl_exposure_list,
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












