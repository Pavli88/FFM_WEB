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

    trades = Trades.objects.filter(status="CLOSE").values()
    trade_df = pd.DataFrame(list(trades))
    pnls = list(trade_df["open_price"]-trade_df["close_price"])
    pnl_label = [label for label in range(len(pnls))]
    cum_pnl = cumulative(pnls)

    print(pnls)
    print(pnl_label)
    print("Cum PNL:", cum_pnl)

    return render(request, 'home.html', {"pnls": pnls,
                                         "pnl_label": pnl_label,
                                         "cum_pnl": cum_pnl})













