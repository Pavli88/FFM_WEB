from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from robots.models import *
from portfolio.models import *
from robots.processes.robot_processes import *
from mysite.processes.oanda import *
from accounts.models import *


# Main site for robot configuration
def robots_main(request):

    print("===============")
    print("ROBOT MAIN PAGE")
    print("===============")

    robots = Robots.objects.filter().values()

    return render(request, 'robots_app/create_robot.html', {"robots": robots})


def create_robot(request):

    """
    This function creates new robot entry in the data base
    :param request:
    :return:
    """

    if request.method == "POST":

        print("==================")
        print("NEW ROBOT CREATION")
        print("==================")

        robot_name = request.POST.get("robot_name")
        strategy_name = request.POST.get("strategy_name")
        security = request.POST.get("security")
        broker = request.POST.get("broker")
        status = request.POST.get("status")
        env = request.POST.get("env")
        time_frame = request.POST.get("time_frame")
        account_number = request.POST.get("account_number")
        sl_policy = request.POST.get("sl_policy")
        precision = request.POST.get("precision")
        pyramiding_level = float(request.POST.get("pyramiding_level"))
        init_exp = float(request.POST.get("init_exp"))
        quantity = float(request.POST.get("quantity"))

        try:
            Robots(name=robot_name,
                   strategy=strategy_name,
                   security=security,
                   broker=broker,
                   status=status,
                   pyramiding_level=pyramiding_level,
                   in_exp=init_exp,
                   env=env,
                   quantity=quantity,
                   time_frame=time_frame,
                   account_number=account_number,
                   sl_policy=sl_policy,
                   prec=precision).save()

            print("Inserting new robot to database")

            Balance(robot_name=robot_name,
                    daily_pnl=0.0,
                    daily_cash_flow=0.0).save()

            print("Setting up initial balance to 0")

            Instruments(instrument_name=robot_name,
                        instrument_type="Robot",
                        source="ffm_system").save()

            print("Saving down robot to instruments table")

        except:
            print("Robot exists in database")
            return render(request, 'robots_app/create_robot.html', {"robot_exists": "yes"})

        return redirect('robots main')


def get_all_robots(request):

    """
    Queries out all robots from database and passes it back to the html
    :param request:
    :return:
    """

    print("Request received to load all robot data on Robots page.")
    print("Loading robot data")

    robots = Robots.objects.filter().values()

    print("ROBOTS:")
    print(robots)

    # Create code to give the data back in json
    if len(robots) == 0:
        return render(request, 'robots_app/create_robot.html')
    else:
        return render(request, 'robots_app/create_robot.html', {"robots": robots})


def delete_robot(request):

    """
    Deletes existing robot from database
    :param request:
    :return:
    """

    print("")
    print("============")
    print("DELETE ROBOT")
    print("============")

    if request.method == "POST":

        message = request.body
        message = str(message.decode("utf-8"))

        robot_id = request.POST.get("robot_id")

        print("Robot ID:", robot_id)
        print("Deleting from database...")

        Robots.objects.filter(id=robot_id).delete()

        print("Record has been deleted")

    return render(request, 'robots_app/create_robot.html', {"robots": Robots.objects.filter().values()})


def amend_robot(request):

    if request.method == "POST":

        """
        Function to amend existing robot data in the database.
        """
        message = request.body
        message = str(message.decode("utf-8"))

        # Gets data from html table
        robot_name = request.POST.get("robot_name")
        env = request.POST.get("env")
        status = request.POST.get("status")
        pyramiding_level = request.POST.get("pyramiding_level")
        init_exp = request.POST.get("init_exp")
        quantity = request.POST.get("quantity")
        account_number = request.POST.get("account_number")
        precision = request.POST.get("precision")

        print("Request received to amend robot record for", robot_name)
        print("New Robot Parameters:")
        print("Robot Name:", robot_name)
        print("Environment:", env)
        print("Status:", status)
        print("P Level:", pyramiding_level)
        print("Initial Exp:", init_exp)
        print("Quantity:", quantity)
        print("Account Number:", account_number)
        print("Precision:", precision)

        # Retrieves back amended robot info and refreshes table
        robot = Robots.objects.get(name=robot_name)
        robot.quantity = quantity
        robot.env = env
        robot.status = status
        robot.pyramiding_level = pyramiding_level
        robot.init_exp = init_exp
        robot.quantity = quantity
        robot.account_number = account_number
        robot.prec = precision
        robot.save()
        print("Amended parameters were saved to database.")

        return render(request, 'robots_app/create_robot.html', {"robots": Robots.objects.filter().values()})


def robot_process_hub(request):
    print("=================")
    print("ROBOT PROCESS HUB")
    print("=================")

    if request.method == "POST":
        process = request.POST.get("process")
        robot = request.POST.get("robot")
        date = request.POST.get("date")

    print("PROCESS:", process)
    print("ROBOT:", robot)
    print("DATE:", date)

    if process == "Balance":
        balance_calc(robot=robot, calc_date=date)

    response = {"securities": [0]}

    print("Sending data to front end")

    return JsonResponse(response, safe=False)


@csrf_exempt
def incoming_trade(request):

    print("===============")
    print("INCOMING SIGNAL")
    print("===============")

    if request.method == "POST":

        # This is for live signal !
        # message = request.body
        # message = str(message.decode("utf-8"))
        # signal = message.split()

        # Test singal
        signal = str(request.POST.get("mydata")).split()

        print("INCOMING SIGNAL:", signal)
        print("ROBOT NAME:", signal[0])
        print("Fetching robot parameters from database")
        print("")

        try:
            robot = Robots.objects.filter(name=signal[0]).values()
            security = robot[0]["security"]
            broker = robot[0]["broker"]
            status = robot[0]["status"]
            account_number = robot[0]["account_number"]
        except:
            print("Robot is not in the database. Execution stopped!")
            return HttpResponse(None)

        print("-------------------------")
        print("Robot database parameters")
        print("-------------------------")
        print("STATUS:", status)
        print("BROKER:", broker)
        print("SECURITY:", security)
        print("ACCOUNT NUMBER:", account_number)

        if status == "inactive":
            print("Robot is inactive. Trade execution stopped!")
            return HttpResponse(None)

        print("Robot is active. Trading is allowed.")
        print("-------------------------")
        print("")
        print("-------------------------")
        print(" ORDER ROUTING TO BROKER ")
        print("-------------------------")

        if broker == "oanda":
            print("Fetching out account parameters from database")

            account = BrokerAccounts.objects.filter(account_number=account_number,
                                                    broker_name=broker).values()

            env = account[0]["env"]

            if env == "demo":
                environment = "practice"
            else:
                environment = "live"


            token = account[0]["access_token"]

            print("ACCOUNT NUMBER:", account_number)
            print("ENVIRONMENT:", environment)
            print("TOKEN:", token)

            print("-------------------------")
            print("     CREATING ORDER      ")
            print("-------------------------")

            trade_side = signal[4]

            print("TRADE SIDE:", trade_side)

            if trade_side == "BUY":
                quantity = str(signal[2])
            elif trade_side == "SELL":
                quantity = str(signal[2] * -1)
            elif trade_side == "Close":

                print("OPEN TRADES:")
                open_trades = pd.DataFrame(list(RobotTrades.objects.filter(robot=signal[0], status="OPEN").values()))
                print(open_trades)
                print("Closing all trades for", signal[0])

                if len(open_trades) == 0:
                    print("There are no open trades for this robot in the database. Execution stopped!")
                    return HttpResponse(None)

                for id, trd in zip(open_trades["id"], open_trades["broker_id"]):
                    print("Close -> OANDA ID:", trd)
                    open_trade = OandaV20(access_token=token,
                                          account_id=account_number,
                                          environment=environment).close_trades(trd_id=trd)
                    print("Update -> Database ID:", id)

                    trade_record = RobotTrades.objects.get(id=id)
                    trade_record.status = "CLOSED"
                    trade_record.close_price = open_trade["price"]
                    trade_record.pnl = open_trade["pl"]
                    trade_record.save()

                return HttpResponse(None)

            print("QUANTITY:", quantity)
            print("ORDER TYPE: MARKET")
            print("SECURITY:", security)
            print("Submiting trade request to Oanda...")

            trade = OandaV20(access_token=token,
                             account_id=account_number,
                             environment=environment).submit_market_order(security=security, quantity=quantity)

            print("Updating robot trade table with new trade record")

            RobotTrades(security=security,
                        robot=signal[0],
                        quantity=quantity,
                        status="OPEN",
                        pnl=0.0,
                        open_price=trade["price"],
                        side=trade_side,
                        broker_id=trade["id"],
                        broker="oanda").save()

            print("Robot trade table is updated!")

    response = {"securities": [0]}

    print("Sending data to front end")

    return JsonResponse(response, safe=False)
