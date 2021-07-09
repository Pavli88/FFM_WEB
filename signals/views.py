# Django imports
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from mysite.my_functions.general_functions import *

# Time imports
from datetime import datetime

# Process imports
from robots.processes.robot_balance_calc import *
from mysite.processes.oanda import *

# Trade functions imports
from signals.functions.trade_functions import *

# Model imports
from accounts.models import *
from robots.models import *
from mysite.models import *
from risk.models import *


def close_trade(robot, account_number, broker, environment, token=None):

    print("*** CLOSE TRADE SIGNAL ***")
    print(" OPEN TRADES")

    open_trades = pd.DataFrame(RobotTrades.objects.filter(robot=robot).filter(status='OPEN').values())

    print(open_trades)

    # Open trade check
    if len(open_trades) == 0:
        print("There are no open trades for this robot in the database. Execution stopped!")
        SystemMessages(msg_type="Trade Execution",
                       msg=robot + ": Close trade request. There are no open trades.").save()
        return None

    if broker == "oanda":
        if environment == "demo":
            environment = "practice"

        print("Closing all trades at Oanda")

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
            trade_record.close_time = get_today()
            trade_record.save()

            SystemMessages(msg_type="Trade Execution",
                           msg="CLOSE: " + robot + " - P&L - " + str(open_trade["pl"])).save()

        print("Calculating balance for robot")

        balance_calc_msg = balance_calc(robot=robot, calc_date=get_today())

        print(balance_calc_msg)


@csrf_exempt
def incoming_trade(request):
    print("*** TRADE SIGNAL ***")

    if request.method == "POST":

        message = request.body
        message = str(message.decode("utf-8"))
        signal = message.split()

        print(" INCOMING SIGNAL:", signal)

        trade_type = signal[1]
        robot = signal[0]
        stop_loss = signal[2]

        print(" ROBOT -", robot, "- TRADE TYPE -", trade_type, "STOP LOSS -", stop_loss)

        # ROBOT INFORMATION ********************************************************************************************
        try:
            robot_data = Robots.objects.filter(name=robot).values()[0]
            security = robot_data["security"]
            status = robot_data["status"]
            environment = robot_data["env"]
            broker = robot_data["broker"]
            account_number = robot_data["account_number"]

            print("")
            print("ROBOT INFORMATION")
            print(" Security -", security)
            print(" Status -", status)
            print(" Environment -", environment)
            print("")
            print("BROKER INFORMATION")
            print(" Broker -", broker)
            print(" Account Number -", account_number)
        except:
            print(" Robot is not in the database. Execution stopped!")
            return HttpResponse(None)

        # Checking if robot is active
        if status == "inactive":
            print(" Robot is inactive. Trade execution stopped!")
            SystemMessages(msg_type="Trade Execution", msg=robot + ": Inactive Robot. Execution stopped.").save()
            return HttpResponse(None)

        # ACCOUNT INFORMATION ******************************************************************************************
        account_data = BrokerAccounts.objects.filter(account_number=account_number).values()[0]
        print(account_data)
        token = account_data["access_token"]

        # Checking if trade is a new execution or a trade close
        if trade_type == "Close":
            close_trade(robot=robot, account_number=account_number, broker=broker, environment=environment, token=token)
            return HttpResponse(None)

        # BALANCE INFORMATION ******************************************************************************************
        balance_params = Balance.objects.filter(robot_name=robot, date=get_today()).values()
        print(balance_params)
        # Check if balance is calculated for a robot
        if not balance_params:
            print(" " + robot + ": Not calculated balance" + " on " + str(get_today()) + ". Execution stopped")

            SystemMessages(msg_type="Trade Execution",
                           msg=robot + ": Not calculated balance" + " on " + str(
                               get_today()) + ". Execution stopped").save()

            return HttpResponse(None)

        # Balance main variable
        balance = balance_params[0]["close_balance"]
        daily_return = balance_params[0]["ret"]
        print(balance)
        # Zero balance check
        if balance == 0.0:
            print(" " + robot + ": Zero balance" + " on " + str(get_today()) + ". Execution stopped")

            SystemMessages(msg_type="Trade Execution",
                           msg=robot + ": Zero balance" + " on " + str(
                               get_today()) + ". Execution stopped. Please fund the robot for trading.").save()

            return HttpResponse(None)

        print("")
        print("BALANCE INFORMATION")
        print(" Balance -", balance)
        print(" Daily Return -", daily_return)

        # RISK CHECK PART **********************************************************************************************
        risk_params = RobotRisk.objects.filter(robot=robot).values()[0] #get_robot_risk_data(robot=robot)[0]

        # Checking if risk parameters are existing for the robot
        if not risk_params:
            print(" Risk parameters are not assigned to the robot. Execution stopped.")

            SystemMessages(msg_type="Trade Execution",
                           msg="Risk parameters are not assigned to " + signal[0] + str(". Execution stopped.")).save()

            return HttpResponse(None)

        # Risk main variables
        daily_risk_perc = risk_params["daily_risk_perc"]*-1
        daily_trade_limit = risk_params["daily_trade_limit"]
        risk_per_trade = risk_params["risk_per_trade"]
        pyramiding_level = risk_params["pyramiding_level"]
        quantity_type = risk_params["quantity_type"]
        quantity_value = risk_params["quantity"]

        print("")
        print("RISK PARAMETERS")
        print(" Daily Risk Limit -", daily_risk_perc)
        print(" Daily Trade Limit -", daily_trade_limit)
        print(" Risk per Trade -", risk_per_trade)
        print(" Pyramiding Level -", pyramiding_level)
        print(" Quantity Type -", quantity_type)
        print(" Quantity Value -", quantity_value)

        # Daily risk limit parameter check
        if daily_risk_perc == 0.0:
            print(robot + ": Trading is not allowed. Daily risk limit is not set for the robot.")

            SystemMessages(msg_type="Risk",
                           msg=robot + ": Trading is not allowed. Daily risk limit is not set for the robot.").save()

            return HttpResponse(None)

        # Daily risk perc parameter check
        if risk_per_trade == 0.0:
            print(robot + ": Trading is not allowed. Daily risk per trade is not set for the robot.")

            SystemMessages(msg_type="Risk",
                               msg=robot + ": Trading is not allowed. Daily risk per trade is not set for the robot.").save()

            return HttpResponse(None)

        # Fetching out robot trades for the current day
        robot_trades = RobotTrades.objects.filter(robot=robot).filter().filter(open_time=get_today()).values() #get_robot_trades(robot=robot, open_time=get_today())

        print("")
        print("TRADES")
        print(" Number of open trades -", robot_trades.count())

        # Daily loss % check
        if daily_return < daily_risk_perc:
            print(robot + ": Trading is not allowed. Daily loss limit is over " + str(daily_risk_perc*100) + "%")

            SystemMessages(msg_type="Risk",
                           msg=robot + ": Trading is not allowed. Daily loss limit is over " + str(daily_risk_perc*100) + "%").save()

            return HttpResponse(None)

        # Number of trades check
        if robot_trades.count() == daily_trade_limit and trade_type != "Close":
            if robot_trades.count() == 0:
                print(robot + ": Trading is not allowed. Daily number of trade limit is not set for the robot.")

                SystemMessages(msg_type="Risk",
                               msg=robot + ": Trading is not allowed. Daily number of trade limit is not set for the robot.").save()
            else:
                print(robot + ": Trading is not allowed. Daily number of trade limit (" + str(robot_trades.count()) +") is reached.")

                SystemMessages(msg_type="Risk",
                               msg=robot + ": Trading is not allowed. Daily number of trade limit (" + str(robot_trades.count()) +") is reached.").save()

            return HttpResponse(None)

        print("Robot passed all risk checks")

        # TRADE EXECUTION PART *****************************************************************************************
        print("")
        print("TRADE EXECUTION")

        if broker == "oanda":

            if environment == "demo":
                environment = "practice"

            print(" Establishing V20 connection at Oanda")
            oanda_connection = OandaV20(access_token=token, account_id=account_number, environment=environment)

            print(" Get market prices for", security)
            prices = oanda_connection.get_prices(instruments=security)

            bid = prices['bids'][0]['price']
            ask = prices['asks'][0]['price']

            print(" BID -", bid, "ASK -", ask)

            if quantity_type == "Fix":
                if trade_type == "BUY":
                    quantity = quantity_value
                elif trade_type == "SELL":
                    quantity = quantity_value*-1
            else:
                if trade_type == "BUY":
                    trade_price = ask
                    if trade_price < stop_loss:
                        print(" Trade price is below stop loss level on BUY trade. Trade cannot be executed.")
                        SystemMessages(msg_type="Trade Execution",
                                       msg=robot + ": Trade price is below stop loss level on BUY trade. Trade cannot be executed.").save()
                        return HttpResponse(None)

                elif trade_type == "SELL":
                    trade_price = bid
                    if trade_price > stop_loss:
                        print(" Trade price is above stop loss level on SELL trade. Trade cannot be executed.")
                        SystemMessages(msg_type="Trade Execution",
                                       msg=robot + ": Trade price is above stop loss level on BUY trade. Trade cannot be executed.").save()
                        return HttpResponse(None)

                print(" Calculating quantity")
                quantity = quantity_calc(balance=balance, risk_per_trade=risk_per_trade,
                                         stop_loss=stop_loss, trade_side=trade_type, trade_price=trade_price)

            if quantity == 0:
                print(" Zero quantity calculated for incoming trade. Trade cannot be executed.")
                SystemMessages(msg_type="Trade Execution",
                               msg=robot + ": Zero quantity calculated for incoming trade. Trade cannot be executed.").save()
                return HttpResponse(None)

            print(" Trade execution via Oanda V20 API")
            trade = oanda_connection.submit_market_order(security=security, quantity=quantity)

            print(" Updating robot trade table with new trade record")

            RobotTrades(security=security,
                        robot=robot,
                        quantity=quantity,
                        status="OPEN",
                        pnl=0.0,
                        open_price=trade["price"],
                        side=trade_type,
                        broker_id=trade["id"],
                        broker="oanda").save()

            print(" Robot trade table is updated!")
            SystemMessages(msg_type="Trade Execution",
                           msg=robot + ": " + str(trade_type) + " " + str(quantity) + " " + str(security)).save()

    response = {"securities": [0]}

    print("Sending data to front end")

    return JsonResponse(response, safe=False)