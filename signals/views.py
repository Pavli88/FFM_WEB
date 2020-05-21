from signals.processes.signal_processes import *
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from robots.processes.robot_processes import *
from mysite.processes.oanda import *
from accounts.models import *
from mysite.models import *
from datetime import datetime


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

        message = "SELL test"
        message = message.split()

        print("")
        print("------------------------------------")
        print("|  ***      TRADE SIGNAL      ***  |")
        print("------------------------------------")

        signal_params = {"trade_side": message[0],
                         "robot_name": message[1]}

        print("Signal received. Parameters:", signal_params)

        now = datetime.now().time()
        print("Current Time:", now)
        print("Checking if new trading is enabled")

        settings = Settings.objects.filter(id=1).values()
        ov_status = settings[0]["ov_status"]
        st_time = settings[0]["ov_st_time"]
        en_time = settings[0]["ov_en_time"]

        print("Restricted Time Status:", ov_status)
        print("Restriction Start Time:", st_time.strftime("%H:%M"))
        print("Restriction End Time:", en_time.strftime("%H:%M"))

        if st_time < now and ov_status is True:
            print("Trading is not allowed due to restricted time period")
            return HttpResponse(None)
        elif now < en_time and ov_status is True:
            print("Trading is not allowed due to restricted time period")
            return HttpResponse(None)
        else:
            print("Trading is not restricted due to time. ")

        print("------------------------")
        print("        Robot info      ")
        print("------------------------")
        print("Looking for robot that is tracking:", signal_params)

        # Gets robot data from database

        try:
            robot = RobotProcesses().get_robot(name=signal_params["robot_name"])
        except:
            print("Robot does not exists in database! Process stopped!")
            return HttpResponse(None)

        quantity = robot[0]["quantity"]

        print("Robot Name:", robot[0]["name"],
              "| Robot ID:", robot[0]["id"],
              "| Robot Status:", robot[0]["status"],
              "| Robot trade size:", quantity)

        trade_side = signal_params["trade_side"]
        security = robot[0]["security"]
        precision = robot[0]["prec"]

        print("")
        print("------------------------")
        print("      Security info     ")
        print("------------------------")
        print("Security:", security,
              "| Trade Side:", trade_side,
              "| Precision:", precision)

        print("")
        print("------------------------")
        print(" Checking robot status ")
        print("------------------------")

        if message[0] == "BUY" or message[0] == "SELL":
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

            print("")
            print("------------------------")
            print("      Broker info       ")
            print("------------------------")

            broker = robot[0]["broker"]
            account_number = robot[0]["account_number"]
            environment = robot[0]["env"]

            print("Broker:", broker,
                  "| Environment:", environment,
                  "| Account Number:", account_number)

            if broker == "oanda":

                print("Retrieving access token for", broker, robot[0]["env"], robot[0]["account_number"])

                # Fetching broker parameters from database

                broker_params = BrokerAccounts.objects.filter(broker_name=broker,
                                                              account_number=account_number,
                                                              env=environment).values()

                try:
                    acces_token = broker_params[0]["access_token"]
                except:
                    print("Broker or account settings are missing in database!")
                    return HttpResponse(None)

                print("Access Token:", acces_token)

                print("")
                print("------------------------")
                print("Creating Oanda connection instance")
                print("------------------------")

                if environment == "demo":
                    oanda_env = "practice"
                else:
                    oanda_env = "live"

                print("Oanda environment:", oanda_env)

                oanda = Oanda(environment=oanda_env,
                              acces_token=acces_token,
                              account_number=account_number)

                print("")

                account_data = oanda.get_account_data()

                # Basic risk parameters -> Later this section will go to risk checking

                daily_risk_limit = 0.10
                starting_balance = 100000.0
                risk_amount = starting_balance * daily_risk_limit
                initial_exposure = robot[0]["in_exp"]

                print("------------------------")
                print("    Risk Parameters     ")
                print("------------------------")
                print("Daily Risk Limit:", daily_risk_limit,
                      "| Start Balance:", starting_balance,
                      "| Risk Amount:", risk_amount,
                      "| Initial Exposure:", initial_exposure)

                print("Checking initial exposure vs daily risk limit:")

                if initial_exposure >= daily_risk_limit:
                    print("Initial exposure is larger than daily risk execution stopped!")
                    return HttpResponse(None)

                print("Initial exposure vs daily risk limit check: Passed")

                # Account balance data

                print("")
                print("------------------------")
                print("   Account Information  ")
                print("------------------------")

                balance = float(account_data["account"]["balance"])
                nav = float(account_data["account"]["NAV"])
                unrealized_pnl = float(account_data["account"]["unrealizedPL"])

                print("Opening Balance:", float(starting_balance),
                      "| Daily Risk Amount:", risk_amount,
                      "| Daily NAV Down Limit:", float(starting_balance) - risk_amount,
                      "| Current NAV:", nav,
                      "| Latest Balance", balance)

                print("")
                print("============================")
                print("   Daily risk limit check   ")
                print("============================")
                # Checking if trade can be executed based on daily risk limit

                if starting_balance - risk_amount > balance:
                    print("You have reached your daily risk limit. Trading is not allowed for this day!")
                    return HttpResponse(None)
                else:
                    print("Trade balance check: Passed")
                print("")

                # Fetching out open positions
                # --> this can be used for risk control later because of the stop lost levels

                print("============================")
                print("      Pyramiding Check      ")
                print("============================")
                print("Fetching out open positions")

                # Cheking pyramiding

                try:
                    open_trades_table = oanda.get_open_trades()
                    open_trades_sec = open_trades_table[open_trades_table["instrument"] == security]
                    open_trade_id_list = len(list(open_trades_table["id"]))
                except:
                    print("There are no open trades on the account.")
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
                                                      balance=balance,
                                                      precision=precision)

                sl = float(order["stopLossOnFill"]["price"])

                if sl < 0:
                    print("Stop Loss level is below 0. Trade execution stopped!")
                    return HttpResponse(None)

                # Submits order to the appropriate account

                print("Sending order to broker")

                try:
                    oanda.submit_order(order=order)
                except:
                    print("Order submission was not successfull.")
                    return HttpResponse(None)

                print("Order was submitted to broker successfully!")

                # Saving trade record to FFM SYSTEM db

                print("Saving open trades data to FFM SYSTEM")

                open_trades = oanda.get_open_trades()[["id", "instrument", "price", ]]

                print("Checking if trade id exists in FFM SYSTEM db")

                for id, open_price in zip(open_trades["id"], open_trades["price"]):

                    print("Oanda ID:", id)
                    print("Open Price:", open_price)

                    trd = Trades.objects.filter(broker_id=id).count()

                    print("FFM SYSTEM Record:", trd)

                    if trd == 0:

                        print("---------")
                        print("Trade does not exists in FFM SYSTEM db")
                        print("Saving trade to db")

                        trade = Trades(security=security,
                                       robot=robot[0]["name"],
                                       quantity=quantity,
                                       strategy=robot[0]["strategy"],
                                       status="OPEN",
                                       open_price=open_price,
                                       time_frame=robot[0]["time_frame"],
                                       side=message[0],
                                       broker=broker,
                                       broker_id=id,
                                       sl=sl,
                                       )
                        trade.save()

                        print("New trade record was saved to FFM SYSTEM db with ID:", id)
                        print("---------")
                    else:
                        print("Trade id exists in FFM SYSTEM db")

        return HttpResponse(None)


@csrf_exempt
def close_all_trades(request):

    """
    This process closes all trades on a security regardless a robot currently
    :param request:
    :return:
    """

    if request.method == "POST":

        message = request.body
        message = str(message.decode("utf-8"))

        # message = "test"

        print("")
        print("------------------------------------------------------------------------")
        print("CLOSE SIGNAL")
        print("------------------------------------------------------------------------")
        print("Closing trades for robot:", message)
        print("Looking for robot in database...")

        # Gets robot data from database
        try:
            robot = RobotProcesses().get_robot(name=message)
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
        security = robot[0]["security"]
        print("Security:", security)
        print("")

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

            if environment == "demo":
                oanda_env = "practice"
            else:
                oanda_env = "live"

            print("Oanda environment:", oanda_env)

            oanda = Oanda(environment=oanda_env,
                          acces_token=acces_token,
                          account_number=account_number)

            print("Fetching out open positions from broker for", security)

            try:
                open_trades_table = oanda.get_open_trades()
                open_trades_sec = open_trades_table[open_trades_table["instrument"] == security]

                # Reaching out oanda for closing positions

                print("Closing positions at Oanda's side")
                oanda.close_all_positions(open_trades_table=open_trades_sec)
                print("Positions have been closed!")

            except:
                print("There are no open positions for this security")
                return HttpResponse(None)

            # Updating FFM SYSTEM db trades

            print("Fetching out open trades from FFM SYSTEM database...")
            trade = Trades.objects.filter(robot=robot[0]["name"],
                                          status="OPEN")

            open_trade_df = pd.DataFrame(list(trade.values()))
            open_trade_id_list = list(open_trade_df["broker_id"])

            print("Open trade IDs in FFM SYSTEM")
            print(open_trade_id_list)

            for id ,trd in zip(open_trade_id_list, trade):

                print("Oanda ID", id)
                print("FFM record", trd.broker_id)
                print("Fetching trade details from Oanda")

                trd_details = oanda.trade_details(trade_id=id)["trade"]

                print("Oanda Close Price", trd_details["averageClosePrice"])
                print(trd_details["realizedPL"])
                print("Updating FFM SYSTEM trade record")

                trd.status = "CLOSE"
                trd.close_price = float(trd_details["averageClosePrice"])
                trd.pnl = float(trd_details["realizedPL"])
                trd.save()

                print("Record has been updated!")
                print("")

        return HttpResponse(None)

