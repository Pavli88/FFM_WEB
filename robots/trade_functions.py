from robots.robot_functions import *
from mysite.processes.oanda import *
from mysite.models import *


def get_open_trades(robot):
    return RobotTrades.objects.filter(robot=robot, status="OPEN").values()


def quantity_calc(balance, stop_loss, trade_side, trade_price):
    pass


def trade_at_oanda(token, account_number, robot, trade_type, environment, security, quantity, sl=None):
    print("Trade execution via Oanda V20 API")
    trade = OandaV20(access_token=token,
                     account_id=account_number,
                     environment=environment).submit_market_order(security=security, quantity=quantity, sl_price=sl)

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
                   msg=robot + ": " + str(trade_type) + " " + str(quantity) + " " + str(security)).save()


# RISK FUNCTIONS
def pyramiding_check(robot):
    pass


def daily_risk_limit_check():
    pass


