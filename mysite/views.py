from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from mysite.forms import RobotParams
from mysite.models import *
from robots.processes.robot_processes import *
import pandas as pd


# Python code to get the Cumulative sum of a list
def cumulative(lists):
    cu_list = []
    length = len(lists)
    cu_list = [sum(lists[0:x:1]) for x in range(0, length+1)]
    return cu_list[1:]


# Home page
def home(request):
    return render(request, 'home.html')


def get_results(request):

    if request.method == "POST":
        trade_side = request.POST.get("side")
        robot_name = request.POST.get("robot_name")

        print("Parameters received:")
        print("Trade Side:", trade_side)

    trades = Trades.objects.filter(status="CLOSE",
                                   side=trade_side,
                                   robot=robot_name).values()

    trade_df = pd.DataFrame(list(trades))

    if trade_df.empty is True:
        print("Empty Dataframe")
        return render(request, 'home.html', {"message": "true"})

    open_prices = list(trade_df["open_price"])
    close_prices = list(trade_df["close_price"])
    units = list(trade_df["quantity"])
    actions = list(trade_df["side"])

    pnls = []

    for open, close, unit, action in zip(open_prices, close_prices, units, actions):
        print(open, close, unit, action)
        if action == "BUY":
            pnl = (open-close)*unit
            pnls.append(pnl)
        elif action == "SELL":
            pnl = ((open-close)*unit)*-1
            pnls.append(pnl)

    pnl_label = [label for label in range(len(pnls))]
    cum_pnl = cumulative(pnls)

    print(pnl_label)
    print("PNLs:", pnls)
    print("Cum PNL:", cum_pnl)

    return render(request, 'home.html', {"pnls": pnls,
                                         "pnl_label": pnl_label,
                                         "cum_pnl": cum_pnl})













