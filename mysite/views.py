from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from mysite.models import *
import pandas as pd
from datetime import date
from datetime import datetime
from robots.models import *
from accounts.models import *
from accounts.account_functions import *
from portfolio.models import *
from mysite.processes.oanda import *
from mysite.processes.calculations import *
from django.http import JsonResponse
from django.contrib.auth.models import User, auth
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from robots.processes.robot_processes import *
from robots.robot_functions import *
from mysite.my_functions.general_functions import *


def test_calc(request):
    print("Loading robot stats to dashboard")

    respo = get_account_balance_history(account="001-004-2840244-004", )

    return JsonResponse([0,0,0], safe=False)


def load_robot_stats(request):
    print("*** Robot Cumulative Performance Calculation ***")

    if request.method == "GET":
        env = request.GET["env"]

    year_beg = beginning_of_year()
    month_beg = beginning_of_month()

    print("Year Start:", year_beg)
    print("Month Start:", month_beg)
    print("")

    # Fetching robots from database based on environment
    robots = Robots.objects.filter(status="active", env=env).values()

    response_data_list = []
    robot_list = []
    dtd_list = []
    mtd_list = []
    ytd_list = []
    balance_list = []
    total_dtd_pnl = 0.0
    total_mtd_pnl = 0.0
    total_ytd_pnl = 0.0

    for robot in robots:

        robot_trades_all = pd.DataFrame(list(Balance.objects.filter(robot_name=robot["name"]).values()))

        yearly_trades = robot_trades_all[robot_trades_all["date"] >= year_beg]
        monthly_trades = robot_trades_all[robot_trades_all["date"] >= month_beg]

        mtd_series = cumulative_return_calc(data_series=monthly_trades["ret"].tolist())
        ytd_series = cumulative_return_calc(data_series=yearly_trades["ret"].tolist())

        last_balance = round(list(robot_trades_all["close_balance"])[-1], 2)

        dtd = round(list(robot_trades_all["ret"])[-1]*100, 2)
        mtd = round(mtd_series[-1]-100, 2)
        ytd = round(ytd_series[-1]-100, 2)

        ytd_pnl = round(total_pnl_calc(yearly_trades["realized_pnl"].tolist()), 2)
        mtd_pnl = round(total_pnl_calc(monthly_trades["realized_pnl"].tolist()), 2)

        try:
            dtd_pnl = round(monthly_trades["realized_pnl"].tolist()[-1], 2)
        except:
            dtd_pnl = 0.0

        total_ytd_pnl = total_ytd_pnl + ytd_pnl
        total_mtd_pnl = total_mtd_pnl + mtd_pnl
        total_dtd_pnl = total_dtd_pnl + dtd_pnl

        robot_list.append(robot["name"])
        dtd_list.append(dtd)
        mtd_list.append(mtd)
        ytd_list.append(ytd)
        balance_list.append(last_balance)
        response_data_list.append({"robot": robot["name"],
                                   "security": robot["security"],
                                   "balance": last_balance,
                                   "dtd": dtd,
                                   "mtd": mtd,
                                   "ytd": ytd,
                                   "ytdPnl": ytd_pnl})

        print(robot["name"], " - YTD PnL", ytd_pnl, " - YTD Ret - ", ytd)
        print(robot["name"], " - MTD PnL", mtd_pnl, " - MTD Ret - ", mtd)
        print(robot["name"], " - DTD PnL", dtd_pnl, " - DTD Ret - ", dtd)
        print(robot["name"], " - Latest Balance - ", last_balance)
        print("")

    print("TOTAL P&L - YTD - ", total_ytd_pnl, " - MTD - ", total_mtd_pnl, " - DTD - ", total_dtd_pnl)
    print("Sending data to front end")

    return JsonResponse({"robots": robot_list,
                         "dtd": dtd_list,
                         "mtd": mtd_list,
                         "ytd": ytd_list,
                         "balance": balance_list,
                         "pnls": [round(total_dtd_pnl, 2), round(total_mtd_pnl, 2), round(total_ytd_pnl, 2)]}, safe=False)

# MAIN PAGE ************************************************************************************************************


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


# **********************************************************************************************************************
# HOME PAGE
# @login_required(login_url="/")
def home(request, default_load=None):
    print("*** HOME PAGE ***")

    return render(request, 'home.html', {"robots": get_robots(status="active"),
                                         "accounts": get_accounts()})


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


def save_layout(request):

    print("Saving home page layout")

    if request.method == "POST":
        account = request.POST.get("account")

    default = HomePageDefault.objects.filter()[0]
    default.account_number = account
    default.save()

    print("Account:", account)

    return redirect('home_page')


# # Settings
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


def get_messages(request):
    print("===================")
    print("GET SYSTEM MESSAGES")
    print("===================")

    if request.method == "GET":
        system_messages = SystemMessages.objects.filter().values()

    response = {"message": list(system_messages)}

    print("Sending data to front end")

    return JsonResponse(response, safe=False)












