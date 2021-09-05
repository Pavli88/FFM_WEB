# Package imports
import pandas as pd
import os
import time
from datetime import date
from datetime import datetime
import datetime
from multiprocessing import Process
import subprocess

from accounts.account_functions import *
from portfolio.models import *
from mysite.processes.oanda import *
from mysite.processes.calculations import *

from robots.robot_functions import *
from mysite.my_functions.general_functions import *
from mysite.processes.return_calculation import *

# Django imports
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.models import User, auth
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django_q.tasks import async_task, result, fetch, delete_cached
from django_q import cluster

# Database imports
from mysite.models import *
from robots.models import *
from accounts.models import *


def load_robot_stats(request, env):
    print("*** Robot Cumulative Performance Calculation ***")

    if request.method == "GET":

        year_beg = beginning_of_year()
        month_beg = beginning_of_month()

        print("Environment:", env)
        print("Year Start:", year_beg)
        print("Month Start:", month_beg)
        print("")

        # Fetching robots from database based on environment
        robots = Robots.objects.filter(status="active", env=env).values()

        response = []
        robot_list = []
        dtd_list = []
        mtd_list = []
        ytd_list = []
        dtd_pnl_list = []
        mtd_pnl_list = []
        ytd_pnl_list = []
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

            dtd = round(list(robot_trades_all["ret"])[-1]*100, 1)
            mtd = round(mtd_series[-1]-100, 1)
            ytd = round(ytd_series[-1]-100, 1)

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
            dtd_pnl_list.append(dtd_pnl)
            mtd_pnl_list.append(mtd_pnl)
            ytd_pnl_list.append(ytd_pnl)
            balance_list.append(last_balance)

            response.append({
                'robot': robot,
                'dtd_ret': dtd,
                'mtd_ret': mtd,
                'ytd_ret': ytd,
                'balance': last_balance,
            })

            print(robot["name"], " - YTD PnL", ytd_pnl, " - YTD Ret - ", ytd)
            print(robot["name"], " - MTD PnL", mtd_pnl, " - MTD Ret - ", mtd)
            print(robot["name"], " - DTD PnL", dtd_pnl, " - DTD Ret - ", dtd)
            print(robot["name"], " - Latest Balance - ", last_balance)
            print("")

        print("TOTAL P&L - YTD - ", total_ytd_pnl, " - MTD - ", total_mtd_pnl, " - DTD - ", total_dtd_pnl)
        print("Sending data to front end")

        return JsonResponse(response, safe=False)


# MAIN PAGE ************************************************************************************************************
def main_page_react(request):
    print("react page")
    return render(request, 'index.html')


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


def system_messages(request):
    print("===================")
    print("GET SYSTEM MESSAGES")
    print("===================")

    if request.method == "GET":
        system_messages = SystemMessages.objects.filter().values()

    response = {"message": list(system_messages)}

    print("Sending data to front end")

    return JsonResponse(response, safe=False)


# Long Running Process Management --------------------------------------------------------------------------------------

def new_task(request):
    print('--------------')
    print("NEW ASYNC TASK")
    print('--------------')

    task_id = async_task(longTask, 1, hook='mysite.views.task_hook', task_name='running task')
    print(task_id)
    print(result(task_id, 200))

    return JsonResponse(list({}), safe=False)


def new_streaming_task(request):
    print('------------------')
    print("NEW STREAMING TASK")
    print('------------------')
    print("Requesting new streaming process")
    p = Process(target=streaming_task, args=(1, 'My command'))
    p.start()
    ProcessInfo(name="My streaming",
                type="streaming",
                pid=p.pid).save()
    print("PROCESS KICKED OFF. PID:", p.pid)

    return JsonResponse(list({}), safe=False)


def stop_task(request):
    print(cluster.Cluster().stop())
    return JsonResponse(list({}), safe=False)


def get_task(request):
    print('FETCH TASK FROM TASK QUEUE')
    task = delete_cached(task_id='2103541c98a54273bbfdc6bac34da39a')
    print(task)
    return JsonResponse(list({}), safe=False)


@csrf_exempt
def kill_streaming_task(request):
    print("----------------------")
    print("KILLING STREAMING TASK")
    print("----------------------")
    if request.method == "POST":
        pid = request.POST["pid"]
        print("PID to kill:", pid)
        p = Process(target=kill_command, args=(pid,))
        p.start()
        print("Updating database")
        process = ProcessInfo.objects.get(pid=pid, is_done=0)
        process.is_done = 1
        process.end_date = datetime.datetime.now()
        process.save()
        return JsonResponse(list({}), safe=False)


def longTask(id, command):
    print("Received task", id)
    print('Command:', command)
    print("Executing task")
    print("PID",os.getpid())


def streaming_task(id, command):
    print("Received task", id)
    print('Command:', command)
    print("Executing task")
    print("PID", os.getpid())
    while True:
        time.sleep(2)
        print(datetime.datetime.now(), os.getpid())


def kill_command(pid):
    subprocess.run('/bin/kill -9 {pid}'.format(pid=pid), shell=True)
    print("Process is killed")













