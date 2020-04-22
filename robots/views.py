from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import os

# Main site for robot configuration
def robots_main(request):
    return render(request, 'robots_app/robots_main.html')

# Trade execution based on Tradingviw feed
@csrf_exempt
def execute_trade(request):

    """
    This function executes trade signals coming from Tradingview.com
    :param request:
    :return:
    """

    if request.method == "POST":

        message = request.body
        print(message.decode("utf-8"))

        env = "practice"
        quantity = 1000
        start_bal = 100000
        sec = "EUR_USD"
        risk_perc = 0.01
        pl = 4
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


# Create new robot
def create_robot(request):
    return render(request, 'robots_app/create_robot.html')

# Test execution
@csrf_exempt
def test_execution(request):

    """
    This function executes trade signals coming from Tradingview.com
    :param request:
    :return:
    """

    if request.method == "POST":

        message = "BUY"

        env = "practice"
        quantity = 1000
        start_bal = 100000
        sec = "EUR_USD"
        risk_perc = 0.01
        pl = 4
        sl_prec = 4

        if message == "BUY":
            os.system('/home/apavlics/FFM_WEB/python_web/venv/bin/python /home/apavlics/FFM_WEB/ffm_web/mysite/processes/execute.py --env {env} --st_bal {start_bal} --sec {sec} --q {quantity} --sl perc --slpv {risk_perc} --pl {pl} --sl_prec {sl_prec}'.format(quantity=quantity, start_bal=start_bal, sec=sec, risk_perc=risk_perc, pl=pl, env=env, sl_prec=sl_prec))
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

