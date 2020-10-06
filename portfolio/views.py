from django.shortcuts import render, redirect
from portfolio.models import *


# Main site for portfolios
def portfolios_main(request):

    portfolios = get_portfolios()

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
        except:
            print("Portfolio exists in database!")

    return render(request, 'portfolios/portfolios_main.html')


def create_instrument(request):

    print("==============")
    print("NEW INSTRUMENT")
    print("==============")

    return redirect('portfolio main')


def get_portfolios():

    """
    Retrieves all portfolio records from database
    :return:
    """

    portfolios = Portfolio.objects.filter().values()

    return portfolios