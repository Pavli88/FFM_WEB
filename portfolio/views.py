from django.shortcuts import render, redirect
from portfolio.models import *
from django.http import JsonResponse


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

    return redirect('portfolio main')


def create_portfolio(request):

    print("======================")
    print("NEW PORTFOLIO CREATION")
    print("======================")

    if request.method == "POST":
        port_name = request.POST.get("port_name")
        port_type = request.POST.get("port_type")

        print("PORTFOLIO NAME:", port_name)
        print("PORTFOLIO TYPE", port_type)

        try:
            Portfolio(portfolio_name=port_name,
                      portfolio_type=port_type).save()
            print("New Portfolio was created!")

            print("Creating nav record for the portfolio")

            Nav(portfolio_name=port_name,
                amount=0.0).save()

        except:
            print("Portfolio exists in database!")

    return redirect('portfolio main')


def create_instrument(request):

    print("==============")
    print("NEW INSTRUMENT")
    print("==============")

    if request.method == "POST":
        instrument_name = request.POST.get("instrument_name")
        instrument_type = request.POST.get("instrument_type")
        source = request.POST.get("source")

        print("INSTRUMENT NAME:", instrument_name)
        print("INSTRUMENT TYPE:", instrument_type)
        print("SOURCE:", source)

        print("Saving new instrument to database")
        Instruments(instrument_name=instrument_name,
                    instrument_type=instrument_type,
                    source=source).save()

        print("New instrument was saved successfully")

    return redirect('portfolio main')


def get_portfolios():

    """
    Retrieves all portfolio records from database
    :return:
    """

    portfolios = Portfolio.objects.filter().values()

    return portfolios


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
        market_value = float(quantity) * float(price)

        if float(quantity) > 0:
            cash_flow = market_value
        else:
            cash_flow = market_value *1

        if security_type == "Robot":
            source = "ffm_system"
        else:
            source = "oanda"

        print("QUANTITY:", quantity)
        print("PRICE:", price)
        print("PORTFOLIO:", portfolio)
        print("SECURITY:", security)
        print("SECURITY TYPE:", security_type)
        print("MARKET VALUE:", market_value)
        print("CASH FLOW:", cash_flow)
        print("SOURCE:", source)

        Trade(portfolio_name=portfolio,
              quantity=quantity,
              price=price,
              mv=market_value,
              sec_type=security_type,
              security=security,
              source=source).save()

        print("Saving new trade record to", portfolio)

        CashFlow(portfolio_name=portfolio,
                 amount=cash_flow,
                 type="TRADE").save()

        print("Amending cash flow table for", portfolio)

    response = {"securities": [0]}

    print("Sending data to front end")

    return JsonResponse(response, safe=False)


def process_hub(request):

    print("=====================")
    print("PORTFOLIO PROCESS HUB")
    print("=====================")

    response = {"securities": [0]}

    print("Sending data to front end")

    return JsonResponse(response, safe=False)

