from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from mysite.forms import RobotParams
from mysite.models import *
from robots.processes.robot_processes import *
import pandas as pd


# Home page
def home(request):
    return render(request, 'home.html')


def get_results(request):

    trades = Trades.objects.filter(status="CLOSE").values()
    trade_df = pd.DataFrame(list(trades))
    pnls = list(trade_df["open_price"]-trade_df["close_price"])
    pnl_label = [label for label in range(len(pnls))]

    print(pnls)
    print(pnl_label)




    return render(request, 'home.html', {"pnls": pnls,
                                         "pnl_label": pnl_label})













