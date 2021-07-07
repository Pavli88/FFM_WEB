from django.shortcuts import render, redirect
from portfolio.models import *
from robots.models import *
from django.http import JsonResponse
from portfolio.processes.processes import *
from robots.processes.robot_processes import *
from instrument.models import *
from datetime import datetime
import datetime
from mysite.models import *
from mysite.my_functions.general_functions import *
from django.views.decorators.csrf import csrf_exempt
from portfolio.portfolio_functions import *
import json
from portfolio.processes.port_pos import *


# CRUD------------------------------------------------------------------------------------------------------------------
@csrf_exempt
def create_portfolio(request):
    print("*** NEW PORTFOLIO CREATION ***")

    if request.method == "POST":
        body_data = json.loads(request.body.decode('utf-8'))
        port_name = body_data["port_name"]
        port_type = body_data["port_type"]
        port_currency = body_data["port_currency"]
        port_code = body_data["port_code"]

        print("PORTFOLIO NAME:", port_name, "PORTFOLIO TYPE:", port_type, "PORTFOLIO CURRENCY", port_currency)

        try:
            Portfolio(portfolio_name=port_name,
                      portfolio_code=port_code,
                      portfolio_type=port_type,
                      currency=port_currency,
                      status="Not Funded").save()

            response = "New Portfolio was created!"

            print("Creating nav record for the portfolio")

            Nav(portfolio_name=port_name).save()

        except:
            response = "Portfolio exists in database!"

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

        return JsonResponse(response, safe=False)


# Portfolio related processes-------------------------------------------------------------------------------------------
@csrf_exempt
def portfolio_trade(request):

    print("===============")
    print("PORTFOLIO TRADE")
    print("===============")

    if request.method == "POST":
        body_data = json.loads(request.body.decode('utf-8'))
        quantity = body_data["unit"]
        price = 1.0 #body_data["price"]
        portfolio = body_data["portfolio"]
        security = body_data["sec"]
        security_type = body_data["sec_type"]
        security_id = body_data["sec_id"]
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
        print("Updating robot and portfolio cash flow tables")
        print('Adding cash flow record to', portfolio)

        CashFlow(portfolio_code=portfolio,
                 amount=market_value * -1,
                 type="TRADE",
                 currency="USD").save()

        if security_type == "Robot":
            print("Adding cash flow record to", security)
            print("ROBOT CASH FLOW:", market_value)

            RobotCashFlow(robot_name=security,
                          cash_flow=market_value).save()

            print("New cash flow was recorded for", security)
            print("Calculating robot balance")

            balance_calc_message = balance_calc(robot=security, calc_date=get_today())

            print(balance_calc_message)

            print("Sending message to system messages table")

            SystemMessages(msg_type="Cash Flow",
                           msg=str(cash_flow * -1) + "cash flow to " + str(security)).save()

        response = 'Portfolio trade was executed successfully!'

        return JsonResponse(response, safe=False)


@csrf_exempt
def pos_calc(request):
    if request.method == "POST":
        print("Incoming request to calculate portfolio positions")
        body_data = json.loads(request.body.decode('utf-8'))
        calc_date = body_data['date']
        portfolio = body_data['portfolio']

        print("Parameters: ", "DATE:", calc_date, "PORTFOLIO:", portfolio)

        portfolio_cositions(portfolio=portfolio, calc_date=calc_date)

        response = "Calc ended"

        return JsonResponse(response, safe=False)


@csrf_exempt
def new_cash_flow(request):
    print("*** PORTFOLIO NEW CASH FLOW ***")

    if request.method == "POST":
        body_data = json.loads(request.body.decode('utf-8'))
        portfolio_name = body_data["port_name"]
        amount = body_data["amount"]
        type = body_data["type"]
        currency = body_data["currency"]

        print("PORTFOLIO NAME:", portfolio_name, "TYPE:", type, "AMOUNT:", amount)

        CashFlow(portfolio_code=portfolio_name,
                 amount=amount,
                 type=type,
                 currency=currency).save()

        print("New cashflow was created!")

        if type == "FUNDING":
            port = Portfolio.objects.get(portfolio_name=portfolio_name)
            port.status = "Funded"
            port.save()
            print("")

        response = "Transaction was recorded successfully!"

    return JsonResponse(response, safe=False)


# Portfolio Group Related Processes-------------------------------------------------------------------------------------
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


