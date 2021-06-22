from django.shortcuts import render, redirect
from portfolio.models import *
from robots.models import *
from django.http import JsonResponse
from portfolio.processes.processes import *
from robots.processes.robot_processes import *
from instrument.models import *
from datetime import datetime
from mysite.models import *
from django.views.decorators.csrf import csrf_exempt
from portfolio.portfolio_functions import *
import json


# URL Processes ********************************************************************************************************
@csrf_exempt
def new_cash_flow(request):
    print("*** PORTFOLIO NEW CASH FLOW ***")

    if request.method == "POST":
        portfolio_name = request.POST.get("port_name")
        amount = request.POST.get("amount")
        type = request.POST.get("type")

        print("PORTFOLIO NAME:", portfolio_name, "TYPE:", type, "AMOUNT:", amount)

        CashFlow(portfolio_name=portfolio_name,
                 amount=amount,
                 type=type).save()

        print("New cashflow was created!")

        if type == "Funding":
            port = Portfolio.objects.get(portfolio_name=portfolio_name)
            port.status = "Funded"
            port.save()
            print("")

    return redirect('portfolio main')


@csrf_exempt
def create_portfolio(request):
    print("*** NEW PORTFOLIO CREATION ***")

    if request.method == "POST":
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)
        port_name = body_data["port_name"]
        port_type = body_data["port_type"]
        port_currency = body_data["port_currency"]

        print("PORTFOLIO NAME:", port_name, "PORTFOLIO TYPE:", port_type, "PORTFOLIO CURRENCY", port_currency)

        try:
            Portfolio(portfolio_name=port_name,
                      portfolio_type=port_type,
                      currency=port_currency,
                      status="Not Funded").save()
            response = "New Portfolio was created!"
        except:
            response = "Portfolio exists in database!"

        print("Creating nav record for the portfolio")

        if port_type == "Portfolio":
            Nav(portfolio_name=port_name).save()

    return JsonResponse(response, safe=False)


def get_portfolio_data(request):

    """
    Function to load portfolio information to front end
    :param request:
    :return:
    """

    print("Request for portfolio data")

    if request.method == "GET":

        portfolio_data = Portfolio.objects.filter().values()

        print("Sending response to front end")

        response = list(portfolio_data)
        print(response)
        return JsonResponse(response, safe=False)


def get_securities_by_type(request):

    print("==============================")
    print("LOADING SECURITIES BY SEC TYPE")
    print("==============================")

    if request.method == "POST":
        security_type = request.POST.get("data")

        print("SECURITY TYPE:", security_type)

        instruments = Instruments.objects.filter(instrument_type=security_type).values()

        print(instruments)

    response = {"securities": list(instruments)}

    print("Sending data to front end")

    return JsonResponse(response, safe=False)


def trade(request):

    print("===============")
    print("PORTFOLIO TRADE")
    print("===============")

    if request.method == "POST":
        quantity = request.POST.get("qty")
        price = request.POST.get("price")
        portfolio = request.POST.get("portfolio")
        security = request.POST.get("sec")
        security_type = request.POST.get("sec_type")
        security_id = request.POST.get("sec_id")
        market_value = float(quantity) * float(price)
        cash_flow = market_value * -1

        if security_type == "Robot":
            source = "ffm_system"
        else:
            source = "oanda"

        print("QUANTITY:", quantity)
        print("PRICE:", price)
        print("PORTFOLIO:", portfolio)
        print("SECURITY:", security)
        print("SECURITY TYPE:", security_type)
        print("SECURITY ID:", security_id)
        print("MARKET VALUE:", market_value)
        print("CASH FLOW:", cash_flow)
        print("SOURCE:", source)

        Trade(portfolio_name=portfolio,
              quantity=quantity,
              price=price,
              mv=market_value,
              sec_type=security_type,
              security=security_id,
              source=source).save()

        print("Saving new trade record to", portfolio)

        CashFlow(portfolio_name=portfolio,
                 amount=cash_flow,
                 type="TRADE").save()

        print("Amending cash flow table for", portfolio)

        if security_type == "Robot":
            print("Amending robot cash flow table")
            print("ROBOT CASH FLOW:", cash_flow * -1)

            RobotCashFlow(robot_name=security,
                          cash_flow=cash_flow * -1).save()

            print("New cash flow was recorded for", security)
            print("Calculating robot balance")

            balance_calc_message = balance_calc(robot=security, calc_date=str(datetime.today().date()))

            print(balance_calc_message)

            print("Sending message to system messages table")

            SystemMessages(msg_type="Cash Flow",
                           msg=str(cash_flow * -1) + "cash flow to " + str(security)).save()

    return redirect('portfolio main')


def process_hub(request):

    print("=====================")
    print("PORTFOLIO PROCESS HUB")
    print("=====================")

    if request.method == "POST":
        process = request.POST.get("process")
        portfolio = request.POST.get("portfolio")
        start_date = request.POST.get("start_date")

        print("PROCESS:", process)
        print("START DATE:", start_date)

    if process == "Positions":
        pos_calc(portfolio=portfolio, calc_date=start_date)
    elif process == "Portfolio Holdings":
        port_holding(portfolio=portfolio, calc_date=start_date)
    elif process == "NAV":
        response = nav_calc(portfolio=portfolio, calc_date=start_date)

    print("Sending data to front end")

    return JsonResponse(response, safe=False)


# Portfolio Group Related Processes
@csrf_exempt
def add_port_to_group(request):
    print("*** PORTFOLIO GROUP ADDITION ***")

    if request.method == "POST":
        parent_id = request.POST.get("process")
        children_id = request.POST.get("process")

        try:
            PortGroup(parent_id=parent_id, children_id=children_id, connection_id=str(parent_id)+str(children_id)).save()
        except:
            response = {"message": "Connection exists in database!"}

    return JsonResponse(response, safe=False)

