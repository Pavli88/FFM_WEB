from django.shortcuts import render, redirect
from mysite.processes.oanda import *

def trade_main(request):
    return render(request, 'trade/trade_main.html')


def submit_trade(request):

    print("================")
    print("NEW MANUAL TRADE")
    print("================")

    OandaV20(access_token="ecd553338b9feac1bb350924e61329b7-0d7431f8a1a13bddd6d5880b7e2a3eea",
                 account_id="101-004-11289420-001").get_open_trades()

    return redirect('trade_app main')
