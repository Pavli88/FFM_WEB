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
        if BrokerAccounts.objects.filter(broker_name=request_data['broker_name'], account_number=request_data['account_number']).exists():
            response = "Account already exists in the database!"
            return JsonResponse(response, safe=False)
        try:
            BrokerAccounts(broker_name=request_data['broker_name'],
                           account_number=request_data['account_number'],
                           account_name=request_data['account_name'],
                           env=request_data['env'],
                           access_token=request_data['token'],
                           currency=request_data['currency'],
                           owner=request_data['owner'],
                           margin_account=request_data['margin_account'],
                           margin_percentage=request_data['margin_percentage']).save()
            response = "Account is created successfully!"
        except:
            response = "Account already exists in the database!"
        return JsonResponse(response, safe=False)


def get_account_data(request, account):
    if request.method == "GET":
        account = BrokerAccounts.objects.filter(broker_name=account).values()
        response = list(account)
        return JsonResponse(response, safe=False)


def get_accounts_data(request):
    if request.method == "GET":
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


def get_accounts(request):
    if request.method == "GET":
        filters = {}
        for key, value in request.GET.items():
            if key in ['broker_name', 'account_number', 'env', 'owner']:
                filters[key] = value
        accounts = BrokerAccounts.objects.filter(**filters).values()
        response = list(accounts)
        return JsonResponse(response, safe=False)


@csrf_exempt
def new_broker(request):
    if request.method == "POST":
        request_data = json.loads(request.body.decode('utf-8'))
        try:
            Brokers(broker=request_data['broker'],
                    broker_code=request_data['broker_code']).save()
            response = 'New broker saved to database!'
        except:
            response = 'Broker code exists in database!'
        return JsonResponse(response, safe=False)


@csrf_exempt
def delete_account(request):
    # Add verification before deleting where the account is held
    if request.method == "POST":
        request_data = json.loads(request.body.decode('utf-8'))
        BrokerAccounts.objects.get(id=request_data['id']).delete()
        response = 'Account is deleted'
        return JsonResponse(response, safe=False)