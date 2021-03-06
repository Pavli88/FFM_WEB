from signals.processes.signal_processes import *
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from robots.processes.robot_processes import *
from mysite.processes.oanda import *
from mysite.models import *


# Test execution
@csrf_exempt
def new_execution(request):

    """
    This function executes trade signals coming from Tradingview.com
    :param request:
    :return:
    """

    if request.method == "POST":

        # message = request.body
        # message = str(message.decode("utf-8"))
        # message = message.split()

        message = "EUR_USD BUY momentum M5 test"
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
        try:
            robot = RobotProcesses().get_robot(name=signal_params["robot_name"])
            print(robot[0])
        except:
            print("Robot does not exists in database! Process stopped!")
            return HttpResponse(None)

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

        if message[0] == robot[0]["security"]:
            pass
        else:
            print("Trade signal was created incorrectly security is not the same that was assigned to the robot!")
            return HttpResponse(None)

        if robot[0]["status"] == "inactive":
            print("Robot is inactive process stopped!")
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
                try:
                    acces_token = broker_params[0]["access_token"]
                except:
                    print("Broker or account settings are missing in database!")
                    return HttpResponse(None)

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
                initial_exposure = robot[0]["in_exp"]

                print("---------------")
                print("Risk Parameters")
                print("---------------")
                print("Daily Risk Limit:", daily_risk_limit)
                print("Start Balance:", starting_balance)
                print("Risk Amount:", risk_amount)
                print("Initial Exposure:", initial_exposure)
                print("Checking initial exposure vs daily risk limit:")
                if initial_exposure >= daily_risk_limit:
                    print("Initial exposure is larger than daily risk execution stopped!")
                    return HttpResponse(None)
                print("Initial exposure vs daily risk limit check: Passed")

                # Account balance data
                print("-------------------")
                print("Account Information")
                print("-------------------")

                balance = float(account_data["account"]["balance"])
                nav = float(account_data["account"]["NAV"])
                unrealized_pnl = float(account_data["account"]["unrealizedPL"])

                print("Opening Balance:", float(starting_balance))
                print("Daily Risk Amount:", risk_amount)
                print("Daily NAV Down Limit:", float(starting_balance) - risk_amount)
                print("Current NAV:", nav)
                print("Latest Balance", balance)
                print("")

                print("Evaluating daily daily risk limit.")
                # Checking if trade can be executed based on daily risk limit
                if starting_balance - risk_amount > balance:
                    print("You have reached your daily risk limit. Trading is not allowed for this day!")
                    return HttpResponse(None)
                else:
                    print("Trade balance check: Passed")
                print("")

                # Fetching out open positions
                # --> this can be used for risk control later because of the stop lost levels
                print("Fetching out open positions...")
                open_trades_table = oanda.get_open_trades()
                open_trades_sec = open_trades_table[open_trades_table["instrument"] == message[0]]
                print(open_trades_sec)
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
                    print("Pyramiding check: Not Passed! Execution stopped!")
                    return HttpResponse(None)

                print("Pyramiding check: Passed")

                # Fetching best bid ask prices
                bid_ask = oanda.bid_ask(security=security)

                # Generating Order
                order = RobotProcesses().create_order(trade_side=trade_side,
                                                      quantity=quantity,
                                                      security=security,
                                                      bid_ask=bid_ask,
                                                      initial_exposure=initial_exposure,
                                                      balance=balance)

                # Saving trade to Database
                print("Saving trade details to database")

                if message[1] == "BUY":
                    open_price = bid_ask["ask"]
                else:
                    open_price = bid_ask["bid"]

                trade = Trades(security=security,
                               robot=robot[0]["name"],
                               quantity=quantity,
                               strategy=robot[0]["strategy"],
                               status="OPEN",
                               open_price=open_price,
                               time_frame=robot[0]["time_frame"],
                               side=message[1]
                               )
                trade.save()

                # Submits order to the appropriate account
                print("Sending order to broker")
                oanda.submit_order(order=order)
                print("Order was submitted successfully!")

        return HttpResponse(None)


@csrf_exempt
def close_all_trades(request):

    if request.method == "POST":

        # message = request.body
        # message = str(message.decode("utf-8"))
        # message = message.split()

        message = "EUR_USD CLOSE_ALL momentum M5 test"
        message = message.split()

        print("")
        print("------------------------------------------------------------------------")
        print("CLOSE SIGNAL")
        print("------------------------------------------------------------------------")

        signal_params = {"security": message[0],
                         "trade_side": message[1],
                         "strategy": message[2],
                         "time_frame": message[3],
                         "robot_name": message[4]}

        print("Signal received. Parameters:", signal_params)
        print("Looking for robot that is tracking:", signal_params)

        # Gets robot data from database
        try:
            robot = RobotProcesses().get_robot(name=signal_params["robot_name"])
            print(robot[0])
        except:
            print("Robot does not exists in database! Process stopped!")
            return HttpResponse(None)

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

        if message[0] == robot[0]["security"]:
            pass
        else:
            print("Trade signal was created incorrectly security is not the same that was assigned to the robot!")
            return HttpResponse(None)

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
            print("Retrieving access token for", broker, robot[0]["env"], robot[0]["account_number"])

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

            print("Fetching out open positions from broker for", message[0])
            open_trades_table = oanda.get_open_trades()
            open_trades_sec = open_trades_table[open_trades_table["instrument"] == message[0]]
            print(open_trades_sec)
            print("")

            print("Fetching out open trades from database...")
            trade = Trades.objects.filter(robot=robot[0]["name"])
            for trd in trade:
                trd.status = "CLOSE"
                trd.save()

            # Reaching out oanda for closing positions
            oanda.close_all_positions(open_trades_table=open_trades_sec)

        return HttpResponse(None)

