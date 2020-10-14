from robots.models import *
import pandas as pd
import numpy as np
import datetime
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
    print("=========================")
    print("ROBOT BALANCE CALCULATION")
    print("=========================")
    print("ROBOT:", robot)
    print("CALCULATION DATE:", calc_date)

    date = datetime.datetime.strptime(calc_date, '%Y-%m-%d')

    trades_df = pd.DataFrame(list(Trades.objects.filter(robot=robot,
                                                       open_time__gte=date).values()))

    print(trades_df)