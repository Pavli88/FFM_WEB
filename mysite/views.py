from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import os

@csrf_exempt
def execute_trade(request):
    if request.method == "POST":

        message = request.body
        print(message.decode("utf-8"))

        quantity = 2000
        start_bal = 181
        risk_perc = 0.01
        pl = 3
        env = "practice"

        if (message.decode("utf-8")) == "BUY":
            os.system('/home/pavliati/python3/project/bin/python /home/pavliati/mysite/codes/python/execute.py --env {env} --st_bal {start_bal} --sec EUR_USD --q {quantity} --sl perc --slpv {risk_perc} --pl {pl}'.format(quantity=quantity, start_bal=start_bal, risk_perc=risk_perc, pl=pl, env=env))
            return HttpResponse(None)
        elif (message.decode("utf-8")) == "SELL":
            os.system('/home/pavliati/python3/project/bin/python /home/pavliati/mysite/codes/python/execute.py --env {env} --st_bal {start_bal} --sec EUR_USD --q -{quantity} --sl perc --slpv {risk_perc} --pl {pl}'.format(quantity=quantity, start_bal=start_bal, risk_perc=risk_perc, pl=pl, env=env))
            return HttpResponse(None)
        elif (message.decode("utf-8")) == "CLOSE":
            os.system('/home/pavliati/python3/project/bin/python /home/pavliati/mysite/codes/python/close_positions.py --ca all --env live')
            return HttpResponse(None)

    if request.method == "GET":
        print("Trade execution")
        return HttpResponse("This site is for trade execution")

def report(request):
    return HttpResponse("Reports")


