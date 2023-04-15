# General imports
import pandas as pd
from mysite.my_functions.general_functions import *

# Model Imports
from robots.models import Robots, RobotTrades, Balance
from risk.models import RobotRisk
from accounts.models import BrokerAccounts

# Process imports
from mysite.processes.oanda import OandaV20


class TradeExecution:
    def __init__(self, robot_id, side=None):
        self.robot = robot_id
        self.side = side
        self.robot_data = Robots.objects.get(id=self.robot)
        self.instrument = self.robot_data.security
        try:
            self.balance = Balance.objects.get(robot_id=self.robot, date=get_today())
            self.account_data = BrokerAccounts.objects.get(account_number=self.robot_data.account_number)
            self.risk_data = RobotRisk.objects.get(robot=self.robot)
            self.quantity = self.risk_data.quantity
            self.connection = OandaV20(access_token=self.account_data.access_token,
                                       account_id=self.account_data.account_number,
                                       environment=self.account_data.env)
            self.connection_status = True
        except Balance.DoesNotExist:
            self.connection_status = False

    def save_trade_to_db(self, open_price, broker_id, quantity):
        RobotTrades(security=self.instrument,
                    robot=self.robot,
                    quantity=quantity,
                    status="OPEN",
                    pnl=0.0,
                    open_price=open_price,
                    side=self.side,
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

    def quantity_calculation(self, stop_level):
        if self.side == "BUY":
            multiplier = 1
        elif self.side == "SELL":
            multiplier = -1
        if self.risk_data.quantity_type == "Fix":
            return self.risk_data.quantity * multiplier
        else:
            if stop_level is None:
                print('Empty stop level')
                return 0
            risk_exposure = self.risk_data.risk_per_trade
            prices = self.connection.get_prices(instruments=self.instrument)
            bid = prices['bids'][0]['price']
            ask = prices['asks'][0]['price']
            price = (float(bid) + float(ask)) / 2
            risked_amount = self.balance.close_balance * risk_exposure
            stop_distance = price-stop_level
            if (self.side == "BUY" and stop_level > price) or (self.side == "SELL" and stop_level < price):
                return 0
            return abs(int(risked_amount/stop_distance)) * multiplier

    def open_trade(self, quantity):
        if quantity == 0:
            print("Invalid trade due to impossible stop handling")
        else:
            trade = self.connection.submit_market_order(security=self.instrument,
                                                        quantity=quantity)
            print(trade)
            if trade['status'] == 'accepted':
                self.save_trade_to_db(open_price=trade['response']["price"],
                                      broker_id=trade['response']['id'],
                                      quantity=quantity)
