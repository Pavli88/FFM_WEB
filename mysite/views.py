# Package imports
import pandas as pd
import os
from time import time, sleep
from datetime import date
from datetime import datetime
import datetime
from multiprocessing import Process
import subprocess
import json
import logging

from accounts.account_functions import *
from portfolio.models import *
from mysite.processes.oanda import *
from mysite.processes.calculations import *

from robots.robot_functions import *
from mysite.my_functions.general_functions import *
from mysite.processes.return_calculation import *
from portfolio.processes.processes import *
# from robots.processes.processes import *

# Django imports
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.models import User, auth
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django_q.tasks import async_task, result, fetch
from django_q.models import Schedule
from django_q.tasks import AsyncTask, Task
from django_q.cluster import *
from django_q.monitor import Stat
from django_q.brokers.orm import ORM
from django.conf import settings
from django.db import connection

# Database imports
from mysite.models import *
from robots.models import *
from accounts.models import *


from robots.processes.run_robot import run_robot


def aggregated_robot_pnl_by_date(request):
    if request.method == "GET":
        env = request.GET.get("env")
        print(env)
        cursor = connection.cursor()
        cursor.execute("""select rb.date, (sum(rb.close_balance)-sum(rb.opening_balance)-sum(rb.cash_flow)) as diff
                            from robots_balance as rb, robots_robots as r
                            where rb.robot_name=r.name
                            and rb.date>='{date}'
                            and r.status='active'
                            and r.env='{env}' group by date;""".format(env=env, date=str(date.today().year)+'-01-01'))
        row = cursor.fetchall()
        response_list = []
        for item in row:
            response_list.append({'x': item[0], 'y': item[1]})
        return JsonResponse(response_list, safe=False)


def aggregated_robot_pnl(request):
    if request.method == "GET":
        start_date = request.GET.get("start_date")
        env = request.GET.get("env")
        cursor = connection.cursor()
        cursor.execute("""select rb.robot_name, (sum(rb.close_balance)-sum(rb.opening_balance)-sum(rb.cash_flow)) as pnl
                            from robots_balance as rb, robots_robots as r
                            where rb.robot_name=r.name
                            and rb.date>='{date}'
                            and status='active'
                            and r.env='{env}' group by rb.robot_name order by pnl desc;""".format(date=start_date, env=env))
        row = cursor.fetchall()
        response_list = []
        for item in row:
            response_list.append({'x': item[0], 'y': round(item[1], 2)})
        return JsonResponse(response_list, safe=False)


def total_robot_pnl(request):
    if request.method == "GET":
        start_date = request.GET.get("start_date")
        env = request.GET.get("env")
        cursor = connection.cursor()
        cursor.execute("""select sum(rb.realized_pnl) as total_pnl
                        from robots_balance rb, robots_robots as r
                        where rb.robot_name=r.name
                        and r.status='active'
                        and r.env='{env}' and rb.date >='{date}';""".format(date=start_date, env=env))
        row = cursor.fetchall()
        if row[0][0] is None:
            response_list = [{'data': 0.0}]
        else:
            response_list = [{'data': round(row[0][0], 2)}]
        return JsonResponse(response_list, safe=False)


def total_robot_balances_by_date(request):
    if request.method == "GET":
        env = request.GET.get("env")
        cursor = connection.cursor()
        cursor.execute("""select rb.robot_name , rb.close_balance as total_pnl
                            from robots_balance rb, robots_robots as r
                            where rb.robot_name=r.name
                            and r.env='{env}'
                            and r.status='active' 
                            and rb.date ='{date}';""".format(date=get_today(), env=env))
        row = cursor.fetchall()
        response_list = []
        for item in row:
            response_list.append({'x': item[0], 'y': item[1]})
        return JsonResponse(response_list, safe=False)


def load_robot_stats(request, env):
    if request.method == "GET":
        year_beg = beginning_of_year()
        month_beg = beginning_of_month()
        robots = Robots.objects.filter(env=env).filter(status='active').values()
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
def system_messages(request, type):
    if request.method == "GET":
        date = request.GET.get("date")
        if type == 'All':
            system_messages = SystemMessages.objects.filter(date=date).order_by('-id').values()
        elif type == 'not_verified':
            system_messages = SystemMessages.objects.filter(date=date).filter(verified=0).order_by('-id').values()
        return JsonResponse(list(system_messages), safe=False)


def verify_system_message(request, msg_id):
    if request.method == "GET":
        msg = SystemMessages.objects.get(id=msg_id)
        msg.verified = 1
        msg.save()

        return JsonResponse(list({}), safe=False)


# Long Running Process Management --------------------------------------------------------------------------------------

def test(request):
    if request.method == "GET":
        robot = request.POST.get("robot")
        run_robot(robot='NATGAS_USD_TRD_M')
        return JsonResponse({'response': 'task executed'}, safe=False)


@csrf_exempt
def new_task(request):
    print("----------------------------------")
    print("SENDING NEW TASK TO BROKER QUEUE  ")
    if request.method == "POST":
        request_data = json.loads(request.body.decode('utf-8'))
        process = request_data["process"]
        task_name = request_data["task_name"]
        arguments = request_data["arguments"]

        print("PROCESS:", process)
        print("TASK NAME:", task_name)
        print("ARGUMENTS:", arguments)

        timeout = 100000

        # Executing task at message broker queue
        task = AsyncTask(process, task_name=task_name, hook=robot_task_hook, timeout=timeout)
        task.args = tuple(arguments)
        task.run()
        SystemMessages(msg_type="Process",
                       msg="Execution: " + task_name).save()
        print("TASK ID:", task.id)
        print("----------------------------------")
        return JsonResponse({'response' : 'task executed'}, safe=False)


@csrf_exempt
def new_schedule(request):
    print("----------------------------------")
    print("          NEW SCHEDULE            ")
    print("----------------------------------")
    if request.method == "POST":
        request_data = json.loads(request.body.decode('utf-8'))
        process = request_data["process"]
        task_name = request_data["task_name"]
        minutes = request_data["minutes"]
        schedule_type = request_data["schedule_type"]
        arguments = "'" + "','".join(str(arg) for arg in request_data["arguments"]) + "'"

        print("PROCESS:", process)
        print("TASK NAME:", task_name)
        print("ARGUMENTS:", str(arguments))
        print("MINUTES:", minutes)
        print("SCHED TYPE:", schedule_type)

        Schedule.objects.create(func=process,
                                args=arguments,
                                schedule_type=schedule_type,
                                name=task_name,
                                minutes=minutes,
                                repeats=-1)

        # logging.basicConfig(format='%(asctime)s %(message)s',
        #                     datefmt='%m/%d/%Y %I:%M:%S %p',
        #                     filename=settings.BASE_DIR + '/process_logs/schedules/' + task_name + '.log',
        #                     filemode='w',
        #                     level=logging.INFO)
        # print(settings.BASE_DIR)
        # logging.info(str(' ').join(['Process:', str(process)]))
        # logging.info(str(' ').join(['Task Name:', str(task_name)]))
        # logging.info(str(' ').join(['Arguments:', str(arguments)]))
        # logging.info(str(' ').join(['Minutes:', str(minutes)]))
        # logging.info(str(' ').join(['Schedule Type:', str(schedule_type)]))

        return JsonResponse({'response': 'schedule executed'}, safe=False)


@csrf_exempt
def delete_schedule(request):
    print("----------------------------------")
    print("         DELETE SCHEDULE          ")
    print("----------------------------------")
    if request.method == "POST":
        request_data = json.loads(request.body.decode('utf-8'))
        task_name = request_data["task_name"]
        Schedule.objects.filter(name=task_name).delete()

        return JsonResponse({'response': 'schedule deleted'}, safe=False)


def robot_task_hook(task):
    print("ROBOT TASK HOOK")
    result = str(task.result).split(".")
    if result[0] == "Timeout":
        print(result[0])
        robot_status = Robots.objects.get(name=result[1])
        robot_status.status = "inactive"
        robot_status.save()
        SystemMessages(msg_type="Process",
                       msg=result[0] + ": " + task.name).save()
    elif result[0] == "Interrupted":
        print(result[0])
        SystemMessages(msg_type="Process",
                       msg=result[0] + ": " + task.name).save()


@csrf_exempt
def update_task(request):
    print("UPDATING RUNNING TASK")
    if request.method == "POST":
        id = request.POST["id"]
        print(id)

        task = fetch(task_id=id)
        print(task)
        print(task.args)
        task.args = ('NEW',)
        print(task.args)
        Task().run

    return JsonResponse(list({}), safe=False)


def delete_task(request):
    print("DELETING TASK FROM BROKER QUEUE")
    if request.method == "POST":
        id = request.POST["id"]
        ORM().delete(task_id=id)
    return JsonResponse(list({}), safe=False)


def get_exceptions(request):
    if request.method == "GET":
        exceptions = Exceptions.objects.filter(entity_code=request.GET.get('entity_code'),
                                               calculation_date=request.GET.get('calculation_date'),
                                               exception_level=request.GET.get('exception_level')).values()
        return JsonResponse(list(exceptions), safe=False)


def update_exception_by_id(request):
    if request.method == "GET":
        exception = Exceptions.objects.get(id=request.GET.get('id'))
        exception.status = request.GET.get('status')
        exception.save()
        return JsonResponse(list(''), safe=False)














