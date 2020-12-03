from django.shortcuts import render, redirect
from portfolio.models import *
from robots.models import *
from django.http import JsonResponse
from portfolio.processes.processes import *
from instrument.models import *


# Main site for portfolios
def portfolios_main(request):

    print("===================")
    print("PORTFOLIO MAIN PAGE")
    print("===================")

    try:
        portfolios = get_portfolios()
        print("Loading portfolios to main page")
    except:
        portfolios = []

    return render(request, 'portfolios/portfolios_main.html', {"portfolios": portfolios})


def new_cash_flow(request):

    print("=============")
    print("NEW CASH FLOW")
    print("=============")

    if request.method == "POST":
        portfolio_name = request.POST.get("port_name")
        amount = request.POST.get("amount")
        type = request.POST.get("type")

        print("PORTFOLIO NAME:", portfolio_name)
        print("TYPE:", type)
        print("AMOUNT:", amount)

        CashFlow(portfolio_name=portfolio_name,
                 amount=amount,
                 type=type).save()

        print("New cashflow was created!")

        if type == "Funding":
            port = Portfolio.objects.get(portfolio_name=portfolio_name)
            port.status = "Funded"
            port.save()

    return redirect('portfolio main')


def create_portfolio(request):

    print("======================")
    print("NEW PORTFOLIO CREATION")
    print("======================")

    if request.method == "POST":
        port_name = request.POST.get("port_name")
        port_type = request.POST.get("port_type")
        port_currency = request.POST.get("port_currency")

        print("PORTFOLIO NAME:", port_name)
        print("PORTFOLIO TYPE", port_type)
        print("PORTFOLIO CURRENCY", port_currency)

        try:
            Portfolio(portfolio_name=port_name,
                      portfolio_type=port_type,
                      currency=port_currency,
                      status="Not Funded").save()

            print("New Portfolio was created!")

            print("Creating nav record for the portfolio")

            Nav(portfolio_name=port_name,
                amount=0.0).save()

        except:
            print("Portfolio exists in database!")

    return redirect('portfolio main')


def get_portfolios(port=None):

    """
    Retrieves all portfolio records from database
    :return:
    """

    if port is None:
        portfolios = Portfolio.objects.filter().values()
    else:
        portfolios = Portfolio.objects.filter(portfolio_name=port).values()

    return portfolios


def get_portfolio_data(request):

    """
    Function to load portfolio information to front end
    :param request:
    :return:
    """

    print("Request for portfolio data")

    if request.method == "GET":
        portfolio = request.GET.get("portfolio")

        print("PORTFOLIO:", portfolio)

        portfolio_data = get_portfolios(port=portfolio)

    print("Sending response to front end")

    response = {"portData": list(portfolio_data)}

    return JsonResponse(response, safe=False)


def load_chart(request):

    print("=========================")
    print("CHART LOADER AND SELECTOR")
    print("=========================")

    if request.method == "POST":
        account = request.POST.get("portfolio")
        print(account)
        print(request.POST.get("chartname"))
        print("Loading Chart")

        response = {"account data": [30, 20, 10, 40]}

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
        quantity = request.POST.get("quantity")
        price = request.POST.get("price")
        portfolio = request.POST.get("portfolio")
        security = request.POST.get("security")
        security_type = request.POST.get("secType")
        security_id = request.POST.get("secId")
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

    response = {"securities": [0]}

    print("Sending data to front end")
    print("")

    return JsonResponse(response, safe=False)


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

    response = {"securities": [0]}

    print("Sending data to front end")

    return JsonResponse(response, safe=False)

