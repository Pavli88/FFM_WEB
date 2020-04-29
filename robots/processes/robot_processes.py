from robots.models import *


class RobotProcesses:

    def __init__(self):

        self.robot = ""

    def get_robot(self, name):

        self.robot = Robots.objects.filter(name=name).values()
        return self.robot

    def create_order(self, trade_side, quantity, security, bid_ask):

        print("Generating order")
        self.bid = bid_ask["bid"]
        self.ask = bid_ask["ask"]

        print("BID:", self.bid)
        print("ASK:", self.ask)
        print("SIDE:", trade_side)
        print("SECURITY:", security)

        if trade_side == "BUY":
            self.units = str(quantity)
        elif trade_side == "SELL":
            self.units = str(quantity * -1)

        print("QUANTITY:", self.units)
        print("Calculation SL")
        print("Checking SL policy...")

        self.order = {"instrument": str(security),
                      "units": self.units,
                      "type": "MARKET",

                 } # "stopLossOnFill": {"price": str(round(sl_level, 4))}

        print("Order:", self.order)

    def close_position(self):
        print("close")