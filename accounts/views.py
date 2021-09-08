from django.shortcuts import render
from django.http import HttpResponse
from accounts.models import *
from accounts.account_functions import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json


@csrf_exempt
def create_broker(request):

    """
    This process creates new broker account record in the broker table.
    :param request:
    :return:
    """

    print("New broker creation request received.")

    if request.method == "POST":
        request_data = json.loads(request.body.decode('utf-8'))
        broker_name = request_data['broker_name']
        account_number = request_data['account_number']
        environment = request_data['env']
        token = request_data['token']
        currency = request_data['currency']

    print("BROKER", broker_name)
    print("ACCOUNT NUMBER", account_number)
    print("ENVIRONMENT", environment)
    print("TOKEN", token)

    try:
        BrokerAccounts(broker_name=broker_name,
                       account_number=account_number,
                       access_token=token,
                       env=environment,
                       currency=currency).save()

        print("Inserting new account to database")

        print("Setting up initial balance to zero")

        response = "Account is created successfully!"
    except:
        print("Account exists in database")
        response = "Account already exists in the database!"

    print("Sending response to front end")
    print("")

    return JsonResponse(response, safe=False)


def get_account_data(request, account):

    """
    Get data for a single account.
    :param request:
    :param account:
    :return:
    """

    print("Get data for a single account.")

    if request.method == "GET":
        account = BrokerAccounts.objects.filter(broker_name=account).values()
        response = list(account)
        print(account)
        print("Sending response to front end")

        return JsonResponse(response, safe=False)


def get_accounts_data(request):
    print("*** GET ACCOUNT DATA ***")
    print("Requesting account data from front end")

    if request.method == "GET":

        broker = request.GET.get("broker")
        env = request.GET.get("env")

        accounts = BrokerAccounts.objects.filter(broker_name=broker).filter(env=env).values()

        response = list(accounts)

        print("Sending response to front end")

        return JsonResponse(response, safe=False)

