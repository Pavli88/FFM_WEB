# General imports
import pandas as pd
from mysite.my_functions.general_functions import *

# Model Imports
from robots.models import Robots, RobotTrades
from risk.models import RobotRisk
from accounts.models import BrokerAccounts

# Process imports
from mysite.processes.oanda import OandaV20


class TradeExecution:
    def __init__(self, robot):
        self.robot = robot
        self.robot_data = Robots.objects.get(name=self.robot)
        self.instrument = self.robot_data.security
        self.account_data = BrokerAccounts.objects.get(account_number=self.robot_data.account_number)
        self.risk_data = RobotRisk.objects.get(robot=self.robot)
        self.quantity = self.risk_data.quantity
        self.connection = OandaV20(access_token=self.account_data.access_token,
                                   account_id=self.account_data.account_number,
                                   environment=self.account_data.env)

    def save_trade_to_db(self, open_price, broker_id, side, quantity):
        RobotTrades(security=self.instrument,
                    robot=self.robot,
                    quantity=quantity,
                    status="OPEN",
                    pnl=0.0,
                    open_price=open_price,
                    side=side,
                    broker_id=broker_id,
                    broker="oanda").save()

    def close_trade(self, ffm_id, broker_id):
        open_trade = self.connection.close_trades(trd_id=broker_id)
        trade_record = RobotTrades.objects.get(id=ffm_id)
        trade_record.status = "CLOSED"
        trade_record.close_price = open_trade["price"]
        trade_record.pnl = open_trade["pl"]
        trade_record.close_time = get_today()
        trade_record.save()

    def close_all_trades(self):
        open_trades = pd.DataFrame(RobotTrades.objects.filter(status='OPEN').filter(robot=self.robot).values())

        if len(open_trades) == 0:
            return None

        for ffm_id, broker_id in zip(open_trades["id"], open_trades["broker_id"]):
            self.close_trade(ffm_id=ffm_id, broker_id=broker_id)

    def open_trade(self, side):
        if side == "BUY":
            multiplier = 1
        elif side == "SELL":
            multiplier = -1
        trade = self.connection.submit_market_order(security=self.instrument,
                                                    quantity=self.quantity * multiplier)
        self.save_trade_to_db(open_price=trade["price"],
                              broker_id=trade['id'],
                              side=side,
                              quantity=self.quantity * multiplier)