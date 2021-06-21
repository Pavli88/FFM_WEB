from django.shortcuts import render
from django.http import HttpResponse
from accounts.models import *
from accounts.account_functions import *
from django.http import JsonResponse
from django.core import serializers

# Accounts main page
def accounts_main(request):
    print("==================")
    print("ACCOUNTS MAIN PAGE")
    print("==================")

    accounts = get_accounts()
    print(accounts)
    return render(request, 'accounts/accounts_main.html', {"accounts": accounts})


def create_broker(request):

    """
    This process creates new broker account record in the broker table.
    :param request:
    :return:
    """

    print("New broker creation request received.")

    if request.method == "POST":
        broker_name = request.POST.get("broker_name")
        account_number = request.POST.get("account_number")
        environment = request.POST.get("env")
        token = request.POST.get("token")

    print("BROKER", broker_name)
    print("ACCOUNT NUMBER", account_number)
    print("ENVIRONMENT", environment)
    print("TOKEN", token)

    try:
        BrokerAccounts(broker_name=broker_name,
                       account_number=account_number,
                       access_token=token,
                       env=environment).save()

        print("Inserting new account to database")

        print("Setting up initial balance to zero")

        AccountBalance(account_number=account_number).save()

        response = "not exists"
    except:
        print("Account exists in database")
        response = "exists"

    print("Sending response to front end")
    print("")

    return JsonResponse(response, safe=False)


def get_accounts():

    """
    Queries out all accounts from database and passes it back to the html
    :param request:
    :return:
    """
    accounts = BrokerAccounts.objects.filter().values()

    return accounts


def get_account_balances():

    balances = AccountBalance.objects.filter().values()

    return balances


def get_account_data(request):
    print("*** GET ACCOUNT DATA ***")
    print("Requesting account data from front end")

    if request.method == "GET":

        broker = request.GET.get("broker")
        env = request.GET.get("env")

        accounts = BrokerAccounts.objects.filter(broker_name=broker).filter(env=env).values()

        print("Sending response to front end")

        return JsonResponse({'accounts': list(accounts)}, safe=False)


def new_cash_flow(request):
    print("*** NEW ACCOUNT CASHFLOW ***")

    if request.method == "POST":
        account = request.POST.get("account")
        cash_flow = request.POST.get("cash_flow")

    print("ACCOUNT", account)
    print("CASH FLOW", cash_flow)
    print("Entering cashflow into the database")

    AccountCashFlow(account_number=account,
                    cash_flow=cash_flow).save()

    response = "New cash flow was entered into the database"

    print("Sending response to front end")

    return JsonResponse(response, safe=False)


# def get_account_data(request, data_type):
#     print("*** GET ACCOUNT DATA REQUEST ***")
#     print("DATA TYPE REQUEST:", data_type)
#
#     if request.method == "GET":
#         account = request.GET.get("account")
#         start_date = request.GET.get("start_date")
#         end_date = request.GET.get("end_date")
#
#     print("ACCOUNT:", account)
#     print("START DATE:", start_date)
#     print("END DATE:", end_date)
#
#     if data_type == "balance":
#         response_data = get_account_balance_history(account=account, start_date=start_date, end_date=end_date)
#
#     response = {"message": list(response_data)}
#
#     print("Sending message to front end")
#
#     return JsonResponse(response, safe=False)