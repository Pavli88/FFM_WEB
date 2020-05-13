from django.shortcuts import render
from django.http import HttpResponse
from accounts.models import *


# Accounts main page
def accounts_main(request):
    return render(request, 'accounts/accounts_main.html')


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
        return render(request, 'accounts/accounts_main.html', {"exist_broker": "Account number exists in data base !"})

    # Inserting new robot data to database
    print("Inserting new record to database")
    robot = BrokerAccounts(broker_name=broker_name,
                           account_number=account_number,
                           access_token=token,
                           env=environment)

    try:
        robot.save()
        print("New record was created with parameters:", string_parameter_dict)
        return render(request, 'accounts/accounts_main.html', {"exist_broker": "created"})
    except:
        print("Error occured while inserting data to database. "
              "Either data type or server configuration is not correct.")
        return render(request, 'accounts/accounts_main.html', {"exist_broker": "issue"})


def get_all_accounts(request):

    """
    Queries out all accounts from database and passes it back to the html
    :param request:
    :return:
    """
    accounts = BrokerAccounts.objects.filter().values()

    header_list = []
    for header in accounts[0]:
        header_list.append(header)

    return render(request, 'accounts/accounts_main.html', {"accounts": accounts})