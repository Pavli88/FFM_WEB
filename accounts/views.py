from django.shortcuts import render
from django.http import HttpResponse
from accounts.models import *
from django.http import JsonResponse


# Accounts main page
def accounts_main(request):
    print("==================")
    print("ACCOUNTS MAIN PAGE")
    print("==================")

    return render(request, 'accounts/accounts_main.html')


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


def load_accounts(request):

    print("Requesting account data from front end")

    accounts = get_accounts()

    response = {"accounts": list(accounts)}

    print("Sending response to front end")

    return JsonResponse(response, safe=False)