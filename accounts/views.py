from django.shortcuts import render
from django.http import HttpResponse
from accounts.models import *
from accounts.account_functions import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json


@csrf_exempt
def create_broker(request):
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
    if request.method == "GET":
        account = BrokerAccounts.objects.filter(broker_name=account).values()
        response = list(account)
        print(account)
        print("Sending response to front end")

        return JsonResponse(response, safe=False)


def get_accounts_data(request):
    if request.method == "GET":
        print(request.GET.items())
        filters = {}
        for key, value in request.GET.items():
            if key in ['broker_name', 'account_number', 'env']:
                filters[key] = value
        accounts = BrokerAccounts.objects.filter(**filters).values()
        response = list(accounts)
        return JsonResponse(response, safe=False)


def get_brokers(request):
    if request.method == "GET":
        brokers = Brokers.objects.all().values()
        return JsonResponse(list(brokers), safe=False)


@csrf_exempt
def new_broker(request):
    if request.method == "POST":
        print('New broker')
        request_data = json.loads(request.body.decode('utf-8'))
        try:
            Brokers(broker=request_data['broker'],
                    broker_code=request_data['broker_code']).save()
            response = 'New broker saved to database!'
        except:
            response = 'Broker code exists in database!'
        return JsonResponse(response, safe=False)