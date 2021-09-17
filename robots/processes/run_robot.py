# General package imports
from time import time, sleep
import datetime
import os
import pandas as pd
import logging
import json

# Database imports
from mysite.models import *
from robots.models import *
from risk.models import *

# Django imports
from django.db import connection
from robots.models import *
from django.conf import settings
from django.core.cache import cache
from django.db.models.signals import post_save
from django.dispatch import receiver

# Process imports
from mysite.processes.oanda import *
from trade_app.processes.close_trade import close_trade_task

# Strategy import
from signals.strategies.market_force_strategy import strategy_evaluate


class RobotExecution:
    def __init__(self, robot):
        self.robot = robot

        # Data soruce is handled on robot level

        # Fetching robot info from database
        cursor = connection.cursor()
        cursor.execute("""select r.id, r.name, r.strategy, r.security,
                                    r.broker, r.status, r.env, r.account_number,
                                    ba.access_token, ri.quantity, ri.quantity_type,
                                    ri.daily_risk_perc,ri.daily_trade_limit, ri.risk_per_trade, r.time_frame
                                from robots_robots as r, accounts_brokeraccounts as ba, risk_robotrisk as ri
                                where r.account_number=ba.account_number
                                and r.name='{robot}' and ri.robot = r.name;""".format(robot=self.robot))
        row = cursor.fetchall()[0]

        robot = row[1]
        strategy = row[2]
        self.instrument = row[3]
        broker = row[4]
        self.status = row[5]
        self.environment = row[6]
        self.account_number = [7]
        self.token = row[8]
        self.time_frame = row[14]
        self.side = "BUY"

        print(robot)
        print(strategy)
        print(self.instrument)
        print(broker)
        print(self.environment)
        print(self.account_number)
        print(self.token)

        # Fetching Risk parameters
        self.risk_params = self.get_risk_params()
        print(self.risk_params)

        if self.time_frame == 'M1':
            self.time_multiplier = 1
        elif self.time_frame == 'M5':
            self.time_multiplier = 5

        print("Time Frame:", self.time_frame)
        print('Time Multiplier:', self.time_multiplier)

        # Setting up broker connection
        module = __import__('mysite.processes')
        print('MODULE', module)
        self.connection = OandaV20(access_token=self.token,
                                   account_id=self.account_number,
                                   environment=self.environment)

        # Requesting initial candle data from broker
        candle_data = self.connection.candle_data(instrument=self.instrument,
                                                  count=500,
                                                  time_frame=self.time_frame)['candles']

        # Setting up initial dataframe
        self.initial_df = self.create_dataframe(data=candle_data)

    def get_candle_data(self, count):
        return self.connection.candle_data(instrument=self.instrument,
                                           count=count,
                                           time_frame=self.time_frame)['candles']

    def create_dataframe(self, data):

        time_list = []
        open_list = []
        close_list = []
        low_list = []
        high_list = []

        for record in data:
            time_list.append(record['time'])
            open_list.append(float(record['mid']['o']))
            close_list.append(float(record['mid']['c']))
            low_list.append(float(record['mid']['l']))
            high_list.append(float(record['mid']['h']))

        df = pd.DataFrame({'time': time_list,
                           'open': open_list,
                           'high': high_list,
                           'low': low_list,
                           'close': close_list})

        return df

    def add_new_row(self, df):
        self.initial_df = self.initial_df.append(df)

    def get_status(self):
        return Robots.objects.get(name=self.robot).status

    def get_risk_params(self):
        return pd.DataFrame(RobotRisk.objects.filter(robot=self.robot).values())

    def get_open_trades(self):
        return pd.DataFrame(RobotTrades.objects.filter(robot=self.robot).filter(status="OPEN").values())

    def execute_trade(self, signal):
        if (self.side == 'BUY' and signal == 'BUY') or (self.side == 'SELL' and signal == 'SELL'):
            print("TRADE EXECUTION:", signal)

            if self.side == "BUY":
                quantity = self.quantity

            # Executing trade at broker
            trade = self.connection.submit_market_order(security=self.instrument, quantity=quantity)

            # Saving executed trade to FFM database
            self.save_trade(quantity=quantity, open_price=trade["price"], broker_id=trade['id'])


        if (self.side == 'BUY' and signal == 'SELL') or (self.side == 'SELL' and signal == 'BUY'):
            print("TRADE EXECUTION:", 'close')

    def close_trade(self):
        return ""

    def save_trade(self, quantity, open_price, broker_id):
        RobotTrades(security=self.instrument,
                    robot=self.robot,
                    quantity=quantity,
                    status="OPEN",
                    pnl=0.0,
                    open_price=open_price,
                    side=self.side,
                    broker_id=broker_id,
                    broker="oanda").save()

    def close_all_trades(self):
        return ""

    def run(self):
        while True:
            # sleep((60 * self.time_multiplier - time() % 60 * self.time_multiplier))
            sleep(2)

            # Checking robot status
            status = self.get_status()
            print("ROBOT STATUS:", status)
            if status == 'inactive':
                print("End of process")
                print("Searching for open trades")
                open_trades = self.get_open_trades()
                print(open_trades)
                if len(open_trades) > 0:
                    print("Closing open trades")
                break

            # Generating Signal based on strategy
            new_candle_data = self.create_dataframe(self.get_candle_data(count=1))
            print(new_candle_data)
            self.add_new_row(df=new_candle_data)
            signal = strategy_evaluate(df=self.initial_df)

            print(self.initial_df.tail(5))

            # Executing Trade
            self.execute_trade(signal=signal)
            print("SIGNAL:", signal)


def run_robot(robot):
    robot_status = Robots.objects.get(name=robot)

    if robot_status.status == "active":
        print("Robot is running")
        return "Robot is already running. End of execution"
    else:
        robot_status.status = "active"
        robot_status.save()
        print("Start of execution")
        RobotExecution(robot=robot).run()


def risk_control(robot, trades_data, current_price, robot_balance, risk_exposure, sl):
    total_pnl = 0.0

    # Loop to look through all open position to evaluate risk checks
    for trade in trades_data:
        print(trade)
        side = trade['side']
        quantity = trade['quantity']
        open_price = trade['open_price']

        if side == "SELL":
            pnl = ((quantity * open_price) - (quantity * current_price)) * -1
        if side == "BUY":
            pnl = (quantity * current_price) - (quantity * open_price)
        total_pnl = + total_pnl + pnl

        # Stop loss check
        if side == "BUY" and float(current_price) < float(sl):
            print("BUY SL Trigger")
            close_trade_task(robot=robot, broker_id=trade['broker_id'])

        if side == "SELL" and float(current_price) > float(sl):
            print("SELL SL Trigger")

    pnl_info = " Total P&L:" + str(total_pnl) + " Total Return:" + str(
        total_pnl / robot_balance) + " Max Risk Loss Exposure:" + str((risk_exposure * -1) * 100)

    print(pnl_info, "SL", sl, "Price", current_price)

    # Loss treshold breached
    if (total_pnl / robot_balance) < (risk_exposure * -1):
        return "Execution stopped. Reason: Risk Controll -> Exposure treshold"


