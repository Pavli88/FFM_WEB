from signals.processes.signal_processes import *
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def incoming_trade_signals(request):

    """
    This process is for capturing incoming trade signal from Tradingview.com
    :param request:
    :return:
    """

    if request.method == "POST":

        message = request.body
        print(message.decode("utf-8"))

    strategy_name = "test_strategy"
    security = "EUR_USD"

    print("-------------------------")
    print("Trade signal was received")
    print("-------------------------")
    print("Signal parameters -> Strategy:", strategy_name, "Security:", security)
    print("Checking if trade signal parameters were assigned to a robot")
    print("Looking for robot in database...")

    signal = TradeSignal(strategy_name=strategy_name, security=security)
    robot = signal.get_robot()

    if robot is False:
        print(strategy_name, "is not assigned to any of the robots in the database! Execution stopped !")
        return render(request, 'robots_app/create_robot.html')

    print("Robot was found with assigned parameters:", strategy_name, security)
    print("Robot name:", robot.name)
    print("Robot status:", robot.status)

    if robot.status == "active":
        print("Generating order...") # ide fogom tovabb irni mit csinaljon ha active
    elif robot.status == "inactive":
        print("Robot is inactive trade signal cannot be executed!")

    return render(request, 'robots_app/create_robot.html')

