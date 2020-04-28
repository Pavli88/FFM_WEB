from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from mysite.forms import RobotParams
from mysite.models import *


# Home page
def home(request):
    robot_form = RobotParams()
    return render(request, 'home.html', {"robot_form": robot_form})


def create_broker(request):

    """
    This process creates new broker account record in the broker table.
    :param request:
    :return:
    """

    print("New broker creation request received.")

    # String fields
    broker_name = request.POST.get("broker_name")
    account_number = request.POST.get("account_number")
    environment = request.POST.get("env")
    token = request.POST.get("token")

    string_parameter_dict = {"broker_name": broker_name,
                             "account_number": account_number,
                             "token": token,
                             "environment": environment,
                             }

    print("Broker parameters:", string_parameter_dict)

    # Checking if robot name exists in data base
    print("Checking if new record exists in database")
    try:
        data_exists = BrokerAccounts.objects.get(account_number=account_number).name
    except:
        data_exists = "does not exist"

    if data_exists == account_number:
        print("Account number exists in database.")
        return render(request, 'robots_app/create_robot.html', {"exist_robots": "Account number exists in data base !"})

    # Inserting new robot data to database
    print("Inserting new record to database")
    robot = BrokerAccounts(broker_name=broker_name,
                           account_number=account_number,
                           access_token=token,
                           env=environment)

    try:
        robot.save()
        print("New record was created with parameters:", string_parameter_dict)
        return render(request, 'home.html', {"exist_robots": "created"})
    except:
        print("Error occured while inserting data to database. "
              "Either data type or server configuration is not correct.")
        return render(request, 'robots_app/create_robot.html',
                      {"exist_robots": "Incorrect data type was given in one of the fields!"})






