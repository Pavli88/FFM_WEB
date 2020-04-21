from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import os

@csrf_exempt
def execute_trade(request):
    if request.method == "POST":

        message = request.body
        print(message.decode("utf-8"))

        env = "live"
        quantity = 1000
        start_bal = 132.94
        sec = "EUR_USD"
        risk_perc = 0.01
        pl = 2
        sl_prec = 4

        if (message.decode("utf-8")) == "BUY":
            os.system('/home/pavliati/python3/project/bin/python /home/pavliati/mysite/codes/python/execute.py --env {env} --st_bal {start_bal} --sec {sec} --q {quantity} --sl perc --slpv {risk_perc} --pl {pl} --sl_prec {sl_prec}'.format(quantity=quantity, start_bal=start_bal, sec=sec, risk_perc=risk_perc, pl=pl, env=env, sl_prec=sl_prec))
            return HttpResponse(None)
        elif (message.decode("utf-8")) == "SELL":
            os.system('/home/pavliati/python3/project/bin/python /home/pavliati/mysite/codes/python/execute.py --env {env} --st_bal {start_bal} --sec {sec} --q -{quantity} --sl perc --slpv {risk_perc} --pl {pl} --sl_prec {sl_prec}'.format(quantity=quantity, start_bal=start_bal, sec=sec, risk_perc=risk_perc, pl=pl, env=env, sl_prec=sl_prec))
            return HttpResponse(None)
        elif (message.decode("utf-8")) == "CLOSE":
            os.system('/home/pavliati/python3/project/bin/python /home/pavliati/mysite/codes/python/close_positions.py --ca all --env live')
            return HttpResponse(None)

    if request.method == "GET":
        print("Trade execution")
        return HttpResponse("This site is for trade execution")

def report(request):
    return HttpResponse("Reports")


