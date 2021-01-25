from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from mysite.models import *
import pandas as pd
from datetime import date
from datetime import datetime
from robots.models import *
from accounts.models import *
from portfolio.models import *
from mysite.processes.oanda import *
from django.http import JsonResponse
from django.contrib.auth.models import User, auth
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from robots.processes.robot_processes import *


# Home page
# @login_required(login_url="/")
def home(request, default_load=None):

    print("=========")
    print("HOME PAGE")
    print("=========")

    if default_load is None:
        print("Loading default settings")
        default_data = HomePageDefault.objects.filter().values()

        if len(default_data) == 0:
            print("No default account has been set.")
            robot_list = []
            broker_account = []
            default_account = "-"
        else:
            default_account = default_data[0]["account_number"]
            broker_account = BrokerAccounts.objects.filter(account_number=default_account).values()[0]
    else:
        print("Loading account parameters for", default_load)

        broker_account = BrokerAccounts.objects.filter(account_number=default_load).values()[0]

    print("Loading robot list from database")
    print("Loading broker account information")

    return render(request, 'home.html', {"dates": get_days(),
                                         "robots": get_robots(),
                                         "open_trades": get_open_trades(),
                                         "accounts": get_account_data(),
                                         "broker": broker_account,
                                         "portfolios": get_portfolios(),
                                         })


def load_robot_stats(request):
    print("Loading robot stats to dashboard")

    if request.method == "GET":
        env = request.GET["env"]

    print(env)
    year_beg = date(date.today().year, 1, 1)
    month_beg = date(date.today().year, date.today().month, 1)

    robots = Robots.objects.filter(status="active", env=env).values()

    response_data_list = []
    dtd_pnl = 0.0
    mtd_pnl = 0.0
    ytd_pnl = 0.0

    for robot in robots:

        balance_calc(robot=robot["name"], calc_date=str(datetime.datetime.today().date()))

        robot_trades_all = pd.DataFrame(list(Balance.objects.filter(robot_name=robot["name"]).values()))

        # Yearly calculations
        try:
            yearly_trades = robot_trades_all[robot_trades_all["date"] > year_beg]
            ytd = 1
            for daily_ret in yearly_trades["ret"]:
                if daily_ret == 0.0:
                    ytd = ytd * 1
                else:
                    ytd = ytd * (daily_ret + 1)
            ytd = str(round((ytd - 1) * 100, 2)) + "%"
            ytd_pnl = ytd_pnl + yearly_trades["realized_pnl"].sum()
        except:
            ytd = 0.0
            ytd_pnl = ytd_pnl + 0.0

        # Monthly calculations
        try:
            monthly_trades = robot_trades_all[robot_trades_all["date"] > month_beg]
            mtd = 1
            for daily_ret in monthly_trades["ret"]:
                if daily_ret == 0.0:
                    mtd = mtd * 1
                else:
                    mtd = mtd * (daily_ret + 1)
            mtd = str(round((mtd - 1) * 100, 2)) + "%"
            mtd_pnl = mtd_pnl + monthly_trades["realized_pnl"].sum()
        except:
            mtd = 0.0
            mtd_pnl = mtd_pnl + 0.0

        try:
            last_balance = round(list(robot_trades_all["close_balance"])[-1], 2)
        except:
            last_balance = 0.0

        # Daily calculations
        try:
            dtd = str(round(list(robot_trades_all["ret"])[-1]*100, 2)) + "%"
            dtd_pnl = dtd_pnl + round(list(robot_trades_all["realized_pnl"])[-1]*100, 2)
        except:
            dtd = 0.0
            dtd_pnl = dtd_pnl + 0.0

        response_data_list.append({"robot": robot["name"], "security": robot["security"],
                                   "env": robot["env"], "balance": last_balance,
                                   "dtd": dtd, "mtd": mtd, "ytd": ytd})

    response = {"robots": response_data_list,
                "pnls": [round(dtd_pnl, 2), round(mtd_pnl, 2), round(ytd_pnl, 2)]}

    print("Sending response to front end")
    print("")

    return JsonResponse(response, safe=False)


def main_page(request):
    print("=========")
    print("MAIN PAGE")
    print("=========")

    if request.user.is_authenticated is True:
        print("User has already logged in")
        print("Redirecting to home page")
        return redirect('home_page')
    else:
        print("Anonimous user! Login is requested!")

    return render(request, 'login.html')


def logout_user(request):

    print("===========")
    print("USER LOGOUT")
    print("===========")
    print("Redirecting to logout page")

    logout(request)
    return redirect('main_page')


def login(request):
    print("==========")
    print("USER LOGIN")
    print("===========")

    if request.method == "POST":
        user_name = request.POST["user"]
        password = request.POST["password"]

        user = auth.authenticate(username=user_name, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('home_page')
        elif user is None:
            print("User is not registered in the database!")
            return redirect('main_page')


def register(request):
    print("============")
    print("REGISTRATION")
    print("============")

    if request.method == "POST":
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        user_name = request.POST["user_name"]
        email = request.POST["new_email"]
        password = request.POST["new_password"]

        print("FIRST NAME:", first_name)
        print("LAST NAME:", last_name)
        print("USER NAME:", user_name)
        print("EMAIL:", email)

        if User.objects.filter(username=user_name).exists():
            print("User exists in database")
        elif User.objects.filter(email=email).exists():
            print("Email exists in database")
        else:
            user = User.objects.create_user(username=user_name,
                                           password=password,
                                           email=email,
                                           first_name=first_name,
                                           last_name=last_name)
            user.save()
            print("New user created!")

        return render(request, 'login.html')


def get_balance_history(start_date, end_date):

    print("")
    print("RETREIVING BALANCE HISTORY FROM BROKER")

    default_account = HomePageDefault.objects.filter().values()
    account = BrokerAccounts.objects.filter(account_number=default_account[0]["account_number"]).values()

    print("Account Number:", default_account[0]["account_number"])
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

    # This part is for Oanda account information
    account_info = oanda.get_account_data()["account"]

    #print(transactions[["accountBalance", "pl"]])

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

    account_dict = {"nav": round(float(account_info["NAV"]), 2),
                    "un_pnl": round(float(account_info["unrealizedPL"]), 2)}

    return balance, balance_label, number_of_trades, trades_dict, account_dict


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


def get_account_data(account_number="All"):

    """
    Function to get all account data
    :return:
    """

    if account_number == "All":
        accounts = BrokerAccounts.objects.filter().values()
    else:
        accounts = BrokerAccounts.objects.filter(account_number=account_number).values()

    return accounts


def get_portfolios():

    """
    Function to get all portfolios
    :return:
    """
    portfolios = Portfolio.objects.filter().values()

    return portfolios


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


def get_robots(account=None, name=None):

    """
    Function to get a list of robots from the db.
    :return:
    """

    print("======================")
    print("      GET ROBOTS      ")
    print("======================")

    if account is None and name is None:
        robots = Robots.objects.filter().values()
    elif account is not None:
        robots = Robots.objects.filter(account_number=account).values()
    elif name is not None:
        robots = Robots.objects.filter(name=name).values()

    # robot_df = pd.DataFrame(list(robots))
    #
    # try:
    #     robot_list = list(robot_df["name"])
    #     robot_list.append("ALL")
    # except:
    #     robot_list = []

    return robots


def get_robot_balance(start_date, end_date, robot=None):

    print("Fetching robot balance data")

    if robot is None:
        robot_balance_data = Balance.objects.filter(date__gte=start_date, date__lte=end_date).values()
    else:
        robot_balance_data = Balance.objects.filter(robot_name=robot, date__range=[start_date, end_date]).values()

    return robot_balance_data


def get_robot_charts_data(request):
    print("=================")
    print("ROBOT CHARTS DATA")
    print("=================")

    if request.method == "GET":
        robot = request.GET.get("robot")
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")
        print("ROBOT:", robot)
        print("START DATE:", start_date)
        print("END DATE:", end_date)

        robot_data = get_robots(name=robot)
        balance = get_robot_balance(robot=robot, start_date=start_date, end_date=end_date)

    response = {"balance": list(balance),
                "robot": list(robot_data)}

    print("Sending response to front end")
    print("")

    return JsonResponse(response, safe=False)


def save_layout(request):

    print("Saving home page layout")

    if request.method == "POST":
        account = request.POST.get("account")

    default = HomePageDefault.objects.filter()[0]
    default.account_number = account
    default.save()

    print("Account:", account)

    return redirect('home_page')


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


def switch_account(request):

    if request.method == "POST":
        account = request.POST.get("data")
        account_data = get_account_data(account_number=account)
        robot_list = get_robots(account=account)

        print(robot_list)

        response = {"account data": list(account_data),
                    "robots": list(robot_list)}

    return JsonResponse(response, safe=False)


def get_messages(request):
    print("===================")
    print("GET SYSTEM MESSAGES")
    print("===================")

    if request.method == "GET":
        system_messages = SystemMessages.objects.filter().values()

    response = {"message": list(system_messages)}

    print("Sending data to front end")

    return JsonResponse(response, safe=False)












