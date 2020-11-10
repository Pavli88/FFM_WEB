from robots.models import *
import pandas as pd
import numpy as np
import datetime
from datetime import timedelta
from mysite.models import *


class RobotProcesses:

    def __init__(self):

        self.robot = ""

    def get_robot(self, name):

        """
        Gets robot parameters from database
        :param name:
        :return:
        """

        self.robot = Robots.objects.filter(name=name).values()
        return self.robot

    def create_order(self, trade_side, quantity, security, bid_ask, initial_exposure, balance, precision):

        """
        Function that generates order based on risk parameters
        :param trade_side:
        :param quantity:
        :param security:
        :param bid_ask:
        :param initial_exposure:
        :param balance:
        :return:
        """

        print("----------------")
        print("Generating order")
        print("----------------")
        print("Checking SL policy.Fetching out risk parameters from database")

        self.bid = bid_ask["bid"]
        self.ask = bid_ask["ask"]

        print("BID:", self.bid)
        print("ASK:", self.ask)
        print("SIDE:", trade_side)
        print("SECURITY:", security)

        if trade_side == "BUY":
            self.units = quantity
        elif trade_side == "SELL":
            self.units = quantity * -1

        print("QUANTITY:", self.units)
        print("Calculation SL")

        # Generating stop loss level
        print("Generating stop loss level")

        sl_risk_amount = balance * initial_exposure

        if self.units > 0:
            sl_level = float(self.ask) - (sl_risk_amount / abs(self.units))
        else:
            sl_level = float(self.bid) + (sl_risk_amount / abs(self.units))

        print("SL Level:", sl_level)
        print("SL Risk Amount:", balance * initial_exposure)

        self.order = {"instrument": str(security),
                      "units": str(self.units),
                      "type": "MARKET",
                      "stopLossOnFill": {"price": str(round(sl_level, precision))}
                      }

        print("Order:", self.order)
        return self.order

    def close_position(self):
        print("close")


def balance_calc(robot, calc_date):

    date = datetime.datetime.strptime(calc_date, '%Y-%m-%d')

    t_min_one_date = date + timedelta(days=-1)

    trades_df_closed = pd.DataFrame(list(RobotTrades.objects.filter(robot=robot,
                                                                    close_time=date,
                                                                    status="CLOSED").values()))

    if trades_df_closed.empty:
        realized_pnl = 0.0
    else:
        realized_pnl = trades_df_closed["pnl"].sum()

    cash_flow_table = pd.DataFrame(list(RobotCashFlow.objects.filter(robot_name=robot,
                                                              date=date).values()))

    if cash_flow_table.empty:
        cash_flow = 0.0
    else:
        cash_flow = cash_flow_table["cash_flow"].sum()

    open_balance_table = pd.DataFrame(list(Balance.objects.filter(robot_name=robot, date=t_min_one_date).values()))

    if open_balance_table.empty:
        message = str(calc_date) + " There is no opening balance data for T-1"
        return message
    else:
        open_balance = open_balance_table["close_balance"].sum()

    close_balance = cash_flow + realized_pnl + open_balance

    ret = realized_pnl / open_balance

    Balance.objects.filter(date=date, robot_name=robot).delete()

    message = "DATE: " + str(calc_date) + " T-1 DATE: " + str(t_min_one_date.date()) + " REALIZED PNL: " + str(round(realized_pnl, 2)) + " CASH FLOW: " + str(cash_flow) + " OPENING BALANCE: " + str(round(open_balance, 2)) + " CLOSING BALANCE: " + str(round(close_balance, 2)) + " RETURN: " + str(round(ret, 4))

    print(message)

    Balance(robot_name=robot,
            opening_balance=round(open_balance, 4),
            close_balance=round(close_balance, 4),
            cash_flow=cash_flow,
            realized_pnl=round(realized_pnl, 4),
            ret=round(ret, 4),
            unrealized_pnl=0.0,
            date=date).save()

    return message
