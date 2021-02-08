from robots.robot_functions import *
from mysite.processes.oanda import *
from mysite.models import *


def get_open_trades(robot):
    return RobotTrades.objects.filter(robot=robot, status="OPEN").values()


def quantity_calc(balance, risk_per_trade, stop_loss, trade_side, trade_price):
    print(" Balance -", balance, "- Risk per Trade -",
          risk_per_trade, "- Stop Loss -", stop_loss,
          "- Trade Side -", trade_side, "- Trade Price -", trade_price)

    risk_amount = balance * risk_per_trade
    price_sl_dist = float(trade_price)-float(stop_loss)
    quantity = int(risk_amount/price_sl_dist)

    print(" Risk Amount -", risk_amount)
    print(" Price and Stop Distance -", price_sl_dist)
    print(" Quantity -", quantity)

    return quantity


# RISK FUNCTIONS
def pyramiding_check(robot):
    pass


def daily_risk_limit_check():
    pass


