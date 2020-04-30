from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from mysite.forms import RobotParams
from mysite.models import *
from robots.processes.robot_processes import *
from mysite.processes.oanda import *
import pandas as pd


# Home page
def home(request):
    robot_form = RobotParams()
    return render(request, 'home.html', {"robot_form": robot_form})


def create_broker(request):

    """
    This process creates new broker account record in the broker table.
    :param request:
    :return:
    """

    print("New broker creation request received.")

    # String fields
    broker_name = request.POST.get("broker_name")
    account_number = request.POST.get("account_number")
    environment = request.POST.get("env")
    token = request.POST.get("token")

    string_parameter_dict = {"broker_name": broker_name,
                             "account_number": account_number,
                             "token": token,
                             "environment": environment,
                             }

    print("Broker parameters:", string_parameter_dict)

    # Checking if robot name exists in data base
    print("Checking if new record exists in database")
    try:
        data_exists = BrokerAccounts.objects.get(account_number=account_number).name
    except:
        data_exists = "does not exist"

    if data_exists == account_number:
        print("Account number exists in database.")
        return render(request, 'robots_app/create_robot.html', {"exist_robots": "Account number exists in data base !"})

    # Inserting new robot data to database
    print("Inserting new record to database")
    robot = BrokerAccounts(broker_name=broker_name,
                           account_number=account_number,
                           access_token=token,
                           env=environment)

    try:
        robot.save()
        print("New record was created with parameters:", string_parameter_dict)
        return render(request, 'home.html', {"exist_robots": "created"})
    except:
        print("Error occured while inserting data to database. "
              "Either data type or server configuration is not correct.")
        return render(request, 'robots_app/create_robot.html',
                      {"exist_robots": "Incorrect data type was given in one of the fields!"})


# Test execution
@csrf_exempt
def test_execution(request):

    """
    This function executes trade signals coming from Tradingview.com
    :param request:
    :return:
    """

    if request.method == "POST":

        message = request.body
        message = str(message.decode("utf-8"))
        message = message.split()

        print("")
        print("------------------------------------------------------------------------")
        print("TRADE SIGNAL")
        print("------------------------------------------------------------------------")

        signal_params = {"security": message[0],
                         "trade_side": message[1],
                         "strategy": message[2],
                         "time_frame": message[3],
                         "robot_name": message[4]}

        print("Signal received. Parameters:", signal_params)
        print("Looking for robot that is tracking:", signal_params)

        # Gets robot data from database
        robot = RobotProcesses().get_robot(name=signal_params["robot_name"])

        print("Db response:", robot)
        print("----------")
        print("Robot info")
        print("----------")
        print("Robot Name:", robot[0]["name"])
        print("Robot Status:", robot[0]["status"])
        quantity = robot[0]["quantity"]
        print("Robot trade size:", quantity)
        print("-------------")
        print("Security info")
        print("-------------")
        trade_side = signal_params["trade_side"]
        security = signal_params["security"]
        print("Security:", security)
        print("Trade Side:", trade_side)
        print("")
        print("Checking robot status...")

        if robot[0]["status"] == "inactive":
            print("robot is inactive process stopped!")
        elif robot[0]["status"] == "active":
            print("Robot is active. Running risk control processes")
            # RISK CONTROL FLOW
            # Here comes the risk control process !

            # If process passed the risk layer order generating process can be started.
            # ORDER GENERATING
            print("Risk control process passed parameters. Starting order generating process")
            print("Checking broker environment paramaters...")
            print("-----------")
            print("Broker info")
            print("-----------")
            broker = robot[0]["broker"]
            print("Broker:", broker)
            account_number = robot[0]["account_number"]
            environment = robot[0]["env"]
            print("Environment:", environment)
            print("Account Number:", account_number)

            if broker == "oanda":
                print("Retrieving access token for", broker, robot[0]["env"],robot[0]["account_number"])

                # Fetching broker parameters from database
                broker_params = BrokerAccounts.objects.filter(broker_name=broker,
                                                              account_number=account_number,
                                                              env=environment).values()

                print("Broker parameters:", broker_params)
                acces_token = broker_params[0]["access_token"]
                print("Access Token:", acces_token)
                print("")
                print("Creating Oanda connection instance")

                oanda = Oanda(environment="practice",
                              acces_token=acces_token,
                              account_number=account_number)

                print("")
                account_data = oanda.get_account_data()

                # Basic risk parameters -> Later this section will go to risk checking
                daily_risk_limit = 0.10
                starting_balance = 100000.0
                risk_amount = starting_balance * daily_risk_limit

                print("---------------")
                print("Risk Parameters")
                print("---------------")
                print("Daily Risk Limit:", daily_risk_limit)
                print("Start Balance:", starting_balance)
                print("Risk Amount:", risk_amount)
                print("")

                # Account balance data
                print("-------------------")
                print("Account Information")
                print("-------------------")

                balance = float(account_data["account"]["balance"])
                nav = float(account_data["account"]["NAV"])
                unrealized_pnl = float(account_data["account"]["unrealizedPL"])
                unrealized_return = round(unrealized_pnl / balance, 3)

                print("Opening Balance:", float(starting_balance))
                print("Daily Risk Amount:", risk_amount)
                print("Daily NAV Down Limit:", float(starting_balance) - risk_amount)
                print("Current NAV:", nav)
                print("Latest Balance", balance)
                print("")

                print("Evaluating daily daily risk limit.")
                # Checking if trade can be executed based on daily risk limit
                if starting_balance - risk_amount > balance:
                    raise Exception("You have reached your daily risk limit. Trading is not allowed for this day!")
                else:
                    print("Trade can be executed ! Balance is not below starting balance.")
                print("")

                # Fetching out open positions
                # --> this can be used for risk control later because of the stop lost levels
                print("Fetching out open positions...")
                open_trades_table = oanda.get_open_trades()
                print("")

                # Cheking pyramiding
                try:
                    open_trade_id_list = len(list(open_trades_table["id"]))
                except:
                    open_trade_id_list = 0

                pyramiding_limit = int(robot[0]["pyramiding_level"])
                print("Number of open trades:", open_trade_id_list)
                print("Pyramiding limit:", pyramiding_limit)

                if int(open_trade_id_list) >= pyramiding_limit:
                    print("New trade breached the pyramiding level execution stopped!")
                    return HttpResponse(None)

                print("New trade did not breach pyramiding limit. Trade can be executed!")

                # Fetching best bid ask prices
                bid_ask = oanda.bid_ask(security=security)

                # Generating Order
                order = RobotProcesses().create_order(trade_side=trade_side,
                                                      quantity=quantity,
                                                      security=security,
                                                      bid_ask=bid_ask)

                # Submits order to the appropriate account
                # .submit_order(order=order)
                print("Order was submitted successfully!")





        return render(request, 'home.html')







