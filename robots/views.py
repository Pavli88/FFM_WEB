from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from robots.models import *
from portfolio.models import *
from robots.processes.robot_processes import *
from mysite.processes.oanda import *
from accounts.models import *
from accounts.account_functions import *
from robots.forms import *
from robots.robot_functions import *
from robots.trade_functions import *
from accounts.models import *
from instrument.models import *
import datetime
from datetime import timedelta, datetime
from risk.models import *
from risk.risk_functions import *
from mysite.models import *
from mysite.my_functions.general_functions import *
from mysite.processes.calculations import *
from instrument.instruments_functions import *


# Main site for robot configuration
def robots_main(request):

    print("===============")
    print("ROBOT MAIN PAGE")
    print("===============")
    print("Loading brokers from database")

    robots = get_robots(status="active")
    robot_form = RobotEntryForm()

    return render(request, 'robots_app/create_robot.html', {"robot_form": robot_form,
                                                            "robots": robots})


def new_robot(request):

    print("==================")
    print("NEW ROBOT CREATION")
    print("==================")

    if request.method == "POST":

        robot_name = request.POST.get("robot_name")
        strategy = request.POST.get("strategy")
        broker = request.POST.get("broker")
        env = request.POST.get("env")
        security = request.POST.get("security")
        account_number = request.POST.get("account")

        print("ROBOT NAME:", robot_name)
        print("STRATEGY:", strategy)
        print("BROKER:", broker)
        print("ENVIRONMENT:", env)
        print("SECURITY:", security)
        print("ACCOUNT:", account_number)

        try:
            Robots(name=robot_name,
                   strategy=strategy,
                   security=security,
                   broker=broker,
                   status="active",
                   env=env,
                   account_number=account_number
                   ).save()

            print("Inserting new robot to database")

            Balance(robot_name=robot_name).save()

            print("Setting up initial balance to 0")

            Instruments(instrument_name=robot_name,
                        instrument_type="Robot",
                        source="ffm_system").save()

            print("Creating new record in robot risk table")

            RobotRisk(robot=robot_name).save()

            print("Saving down robot to instruments table")

            response = {"securities": []}

        except:
            print("Robot exists in database")
            response = {"message": "alert"}

    SystemMessages(msg_type="NEW ROBOT",
                   msg=robot_name + ": New robot was created.").save()

    print("Sending response to front end")
    print("")

    return JsonResponse(response, safe=False)

# ===================================
# Functions to load data to front end
# ===================================


def load_robots(request):

    print("Request from front end to load all robot data")

    robots = get_robots()

    response = {"securities": list(robots)}

    print("Sending data to front end")
    print("")

    return JsonResponse(response, safe=False)


def load_securities(request):
    print("Request from front end to load security data")

    if request.method == "GET":
        broker = request.GET.get("broker")

    print("BROKER:", broker)

    securities = get_securities(broker=broker)

    response = {"securities": list(securities)}

    print("Sending data to front end")
    print("")

    return JsonResponse(response, safe=False)


def load_accounts(request):
    print("Request from front end to load accounts data")

    if request.method == "GET":
        broker = request.GET.get("broker")
        env= request.GET.get("env")

    print("BROKER:", broker)
    print("ENVIRONTMENT:", env)

    accounts = get_accounts(broker=broker, environment=env)

    response = {"accounts": list(accounts)}

    print("Sending data to front end")
    print("")

    return JsonResponse(response, safe=False)

# ===================================
# Functions to get data from database
# ===================================


def get_accounts(broker=None, environment=None):
    if broker is None:
        accounts = BrokerAccounts.objects.filter().values()
    else:
        accounts = BrokerAccounts.objects.filter(broker_name=broker, env=environment).values()

    return accounts


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
        end_date_str = request.POST.get("endDate")

    print("PROCESS:", process)
    print("ROBOT:", robot)
    print("START DATE:", date, )
    print("END DATE:", end_date_str)

    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

    if process == "Balance":

        print("=========================")
        print("ROBOT BALANCE CALCULATION")
        print("=========================")

        if robot == "ALL":
            robot_list = [record["name"] for record in get_robots(status="active")]
        else:
            robot_list = [robot]

        print("ROBOTS:", robot_list)
        print("")

        for active_robot in robot_list:
            print("")
            print(">>> ROBOT:", active_robot)

            start_date = datetime.strptime(date, '%Y-%m-%d').date()

            message_list = []

            while start_date < end_date:
                start_date = start_date + timedelta(days=1)
                process_response = balance_calc(robot=active_robot, calc_date=str(start_date))
                message_list.append(process_response)

                # if process_response != "Calculation is completed!":
                #     break

    response = {"message": message_list}

    print("Sending message to front end")

    return JsonResponse(response, safe=False)


def close_trade(robot):
    print("*** CLOSE TRADE SIGNAL ***")
    print("Fetching robot data for", robot)

    robot_data = get_robots(name=robot)[0]

    print(robot_data)

    account_data = get_account_info(account_number=robot_data["account_number"])[0]

    print(account_data)

    print("Fetching open trades for", robot)
    open_trades = pd.DataFrame(list(get_open_trades(robot=robot)))

    print(open_trades)

    if len(open_trades) == 0:
        print("There are no open trades for this robot in the database. Execution stopped!")
        SystemMessages(msg_type="Trade Execution",
                       msg=robot + ": Close trade request. There are no open trades.").save()
        return HttpResponse(None)


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

        print(" ROBOT -", robot, "- TRADE TYPE -", trade_type, )

        # Checking if trade is a new execution or a trade close
        if trade_type == "Close":
            close_trade(robot=robot)

        # ROBOT INFORMATION ********************************************************************************************
        try:
            robot_data = get_robots(name=robot)[0]
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
            print(robot_data)
        except:
            print(" Robot is not in the database. Execution stopped!")
            return HttpResponse(None)

        # Checking if robot is active
        if status == "inactive":
            print(" Robot is inactive. Trade execution stopped!")
            SystemMessages(msg_type="Trade Execution", msg=robot + ": Inactive Robot. Execution stopped.").save()
            return HttpResponse(None)

        # ACCOUNT INFORMATION ******************************************************************************************
        account_data = get_account_info(account_number=account_number)[0]
        token = account_data["access_token"]
        print(token)
        # BALANCE INFORMATION ******************************************************************************************
        balance_params = Balance.objects.filter(robot_name=robot, date=get_today()).values()[0]

        # Check if balance is calculated for a robot
        if not balance_params:
            print(" " + robot + ": Not calculated balance" + " on " + str(get_today()) + ". Execution stopped")

            SystemMessages(msg_type="Trade Execution",
                           msg=robot + ": Not calculated balance" + " on " + str(
                               get_today()) + ". Execution stopped").save()

            return HttpResponse(None)

        # Balance main variable
        balance = balance_params["close_balance"]
        daily_return = balance_params["ret"]

        print("BALANCE INFORMATION")
        print(" Balance -", balance)
        print(" Daily Return -", daily_return)
        print(balance_params)

        # RISK CHECK PART **********************************************************************************************
        risk_params = get_robot_risk_data(robot=robot)[0]

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

        print("")
        print("RISK PARAMETERS")
        print(" Daily Risk Limit -", daily_risk_perc)
        print(" Daily Trade Limit -", daily_trade_limit)
        print(" Risk per Trade -", risk_per_trade)
        print(" Pyramiding Level -", pyramiding_level)
        print(risk_params)

        # Fetching out robot trades for the current day
        robot_trades = get_robot_trades(robot=robot, date=get_today())[0]

        print(" Fetching balance information from database")

        # Checking if close balance is not zero

        # Daily loss % check
        if daily_return < daily_risk_perc:
            print(robot + ": Trading is not allowed. Daily loss limit is over " + str(daily_risk_perc*100) + "%")

            SystemMessages(msg_type="Risk",
                           msg=robot + ": Trading is not allowed. Daily loss limit is over " + str(daily_risk_perc*100) + "%").save()

            return HttpResponse(None)

        # Number of trades check
        if robot_trades.count() == risk_params[0]["daily_trade_limit"] and trade_type != "Close":
            if robot_trades.count() == 0:
                print(signal[0] + ": Trading is not allowed. Daily number of trade limit is not set for the robot.")

                SystemMessages(msg_type="Risk",
                               msg=signal[0] + ": Trading is not allowed. Daily number of trade limit is not set for the robot.").save()
            else:
                print(signal[0] + ": Trading is not allowed. Daily number of trade limit (" + str(robot_trades.count()) +") is reached.")

                SystemMessages(msg_type="Risk",
                               msg=signal[0] + ": Trading is not allowed. Daily number of trade limit (" + str(robot_trades.count()) +") is reached.").save()

            return HttpResponse(None)

        print("Robot passed all risk checks")

        # TRADE EXECUTION PART *****************************************************************************************

        if broker == "oanda":
            # Quantity calculation

            # Submitting trade

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

            print("TRADE SIDE:", trade_type)

            if trade_type == "BUY":
                quantity = str(signal[2])
            elif trade_type == "SELL":
                quantity = str(int(signal[2]) * -1)
            elif trade_type == "Close":

                print("OPEN TRADES:")
                open_trades = pd.DataFrame(list(RobotTrades.objects.filter(robot=signal[0], status="OPEN").values()))
                print(open_trades)
                print("Closing all trades for", signal[0])

                if len(open_trades) == 0:
                    print("There are no open trades for this robot in the database. Execution stopped!")
                    SystemMessages(msg_type="Trade Execution", msg=signal[0] + ": Close trade request. There are no open trades.").save()
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
                    trade_record.close_time = datetime.today().date()
                    trade_record.save()

                    SystemMessages(msg_type="Trade Execution", msg="CLOSE: " + signal[0] + "P&L " + str(open_trade["pl"])).save()

                print("Calculating balance for robot")

                balance_calc_msg = balance_calc(robot=signal[0], calc_date=str(datetime.today().date()))

                print(balance_calc_msg)

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
                        robot=robot,
                        quantity=quantity,
                        status="OPEN",
                        pnl=0.0,
                        open_price=trade["price"],
                        side=trade_type,
                        broker_id=trade["id"],
                        broker="oanda").save()

            print("Robot trade table is updated!")

            SystemMessages(msg_type="Trade Execution",
                           msg=signal[0] + ": " + str(trade_type) + " " + str(quantity) + " " + str(security)).save()

    response = {"securities": [0]}

    print("Sending data to front end")

    return JsonResponse(response, safe=False)


def delete_robot(request):
    print("============")
    print("DELETE ROBOT")
    print("============")

    if request.method == "POST":
        robot = request.POST.get("robot_name")

    print("ROBOT:", robot)

    print("Deleting robot from database")

    response = {"message": "Robot was deleted"}

    Robots.objects.filter(name=robot).delete()

    print("Sending data to front end")

    return JsonResponse(response, safe=False)


def calculate_robot_balance(request):
    print("-----------------------------")
    print("ROBOT BALANCE CALCULATION JOB")
    print("-----------------------------")
    print("Loading robots from database")

    robots = pd.DataFrame(list(Robots.objects.filter().values()))

    print(robots)
    print("")
    print("Calculating balances")

    for robot in robots["name"]:
        bal_calc_msg = balance_calc(robot=robot, calc_date=str(get_today()))
        print(datetime.now(), bal_calc_msg)

    SystemMessages(msg_type="Robot Balance Calculation",
                   msg="Robot balance calculation job run successfully for all robots at " + str(datetime.now())).save()

    return HttpResponse(None)


# Javascript based calls from front end to transfer robot data
def get_robot_data(request, data_type):
    print("------------------")
    print("ROBOT DATA REQUEST")
    print("------------------")
    print("DATA TYPE REQUEST:", data_type)

    if request.method == "GET":
        robot = request.GET.get("robot")
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")

    print("ROBOT:", robot)
    print("START DATE:", start_date)
    print("END DATE:", end_date)

    if data_type == "balance":
        response_data = get_robot_balance(robot_name=robot)
    elif data_type == "trade":
        response_data = get_robot_trades(robot=robot)
    elif data_type == "cumulative_return":
        balance = pd.DataFrame(list(get_robot_balance(robot_name=robot)))
        response_data = []

        for record in cumulative_return_calc(balance["ret"]):
            response_data.append({"data": record})

    elif data_type == "drawdown":
        raw_data = pd.DataFrame(list(get_robot_balance(robot_name=robot)))
        draw_down_data = drawdown_calc(raw_data["ret"].tolist())

        response_data = []

        for record in draw_down_data:
            response_data.append({"data": record})

    response = {"message": list(response_data)}

    print("Sending message to front end")

    return JsonResponse(response, safe=False)




