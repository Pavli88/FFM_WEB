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

from mysite.my_functions.general_functions import *
from mysite.processes.return_calculation import *


# Django imports
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.models import User, auth
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.db import connection

# Database imports
from mysite.models import *
from accounts.models import *
from portfolio.models import Portfolio

# MAIN PAGE ************************************************************************************************************
def main_page_react(request):
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
    return JsonResponse({'response': 'User logged out!'}, safe=False)


@csrf_exempt
def login_user(request):
    if request.method == "POST":
        ##
        try:
            request_data = json.loads(request.body.decode('utf-8'))
            username = request_data.get("username")
            password = request_data.get("password")

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)

                # Serialize the user data
                user_data = {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "is_staff": user.is_staff,
                    "is_superuser": user.is_superuser,
                    "date_joined": user.date_joined.strftime('%Y-%m-%d %H:%M:%S'),
                    "last_login": user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else None
                }

                return JsonResponse({'userAllowedToLogin': True, 'user': user_data}, safe=False)

            return JsonResponse({'response': 'User is not registered in the database!'}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


@csrf_exempt
def register(request):
    if request.method == "POST":
        request_data = json.loads(request.body.decode('utf-8'))
        user_name = request_data["user_name"]
        if User.objects.filter(username=user_name).exists():
            return JsonResponse({'response': 'User already exists'}, safe=False)
        elif User.objects.filter(email=request_data["email"]).exists():
            return JsonResponse({'response': 'Email already exists'}, safe=False)
        else:
            user = User.objects.create_user(username=user_name,
                                           password=request_data["password"],
                                           email=request_data["email"])
            user.save()
            Portfolio(portfolio_name='Main Portfolio',
                      portfolio_code='MAIN_' + user_name.upper(),
                      portfolio_type='Main',
                      status="active",
                      inception_date=date.today(),
                      owner=user_name).save()
            return JsonResponse({'response': 'Succesfull registration'}, safe=False)


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














