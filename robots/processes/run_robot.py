# General package imports
from time import time, sleep
import datetime
import os
import pandas as pd
import logging
import json
import importlib
from django.core.cache import cache
from mysite.my_functions.general_functions import *

# Database imports
from mysite.models import *
from robots.models import *
from risk.models import *

# Django imports
from django.db import connection
from robots.models import *

# Process imports
from mysite.processes.oanda import *


class RobotExecution:
    def __init__(self, robot, side):
        self.robot = robot

        # Data source is handled on robot level

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

        self.strategy = row[2]
        self.instrument = row[3]
        self.broker = row[4]
        self.status = row[5]
        self.environment = row[6]
        self.account_number = row[7]
        self.token = row[8]
        self.time_frame = row[14]
        self.side = side

        print("")
        print("ROBOT EXECUTION")
        print("Robot:", self.robot, "- Strategy:", self.strategy, "- Instrument:", self.instrument, '- Side:', self.side)

        # Loading strategy and its parameters

        # this goes to a variable and loaded from db
        self.strategy_location = importlib.import_module('signals.strategies.market_force_strategy')
        self.strategy_evaluate = getattr(self.strategy_location, "strategy_evaluate")

        print('Strategy Location:', self.strategy_location)

        if self.time_frame == 'M1':
            self.time_multiplier = 1
        elif self.time_frame == 'M5':
            self.time_multiplier = 5

        print("Time Frame:", self.time_frame)
        print('Time Multiplier:', self.time_multiplier)

        # Setting up broker connection
        # This part has to be loaded with importlib as well in the future to create connection function
        print("Setting up broker connection")
        print("Broker:", self.broker)
        print("Environment:", self.environment)
        print("Account Number", self.account_number)
        print("Token:", self.token)
        self.connection = OandaV20(access_token=self.token,
                                   account_id=self.account_number,
                                   environment=self.environment)

        # Requesting initial candle data from broker
        print("Requesting initial candles from broker")
        candle_data = self.connection.candle_data(instrument=self.instrument,
                                                  count=500,
                                                  time_frame=self.time_frame)['candles']

        # Setting up initial dataframe
        print("Setting up initial dataframe for candle evaluation")
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
        return cache.get(self.robot)

    def get_risk_params(self):
        return RobotRisk.objects.filter(robot=self.robot).values()[0]

    def get_open_trades(self):
        return pd.DataFrame(RobotTrades.objects.filter(robot=self.robot).filter(status="OPEN").values())

    def execute_trade(self, signal):
        # New trade execution
        if (self.side == 'BUY' and signal == 'BUY') or (self.side == 'SELL' and signal == 'SELL'):
            print("TRADE EXECUTION:", signal)

            # Quantity calculation
            quantity = self.quantity_calc()

            # Executing trade at broker
            try:
                trade = self.connection.submit_market_order(security=self.instrument, quantity=quantity)
            except:
                SystemMessages(msg_type="Trade Execution",
                               msg="ERROR - " + self.robot + " - Error during trade execution at broker").save()
                return None

            # Saving executed trade to FFM database
            self.save_new_trade(quantity=quantity, open_price=trade["price"], broker_id=trade['id'])

        # Closing trade execution
        if (self.side == 'BUY' and signal == 'SELL') or (self.side == 'SELL' and signal == 'BUY'):
            print("TRADE EXECUTION:", 'close')
            self.close_all_trades()

    def quantity_calc(self):
        risk_params = self.get_risk_params()
        if risk_params['quantity_type'] == "Fix":
            if self.side == "BUY":
                quantity = risk_params['quantity']
            elif self.side == "SELL":
                quantity = risk_params['quantity'] * -1
        return quantity

    def save_new_trade(self, quantity, open_price, broker_id):
        """
        Saves new trade data to ffm system database
        :param quantity:
        :param open_price:
        :param broker_id:
        :return:
        """
        RobotTrades(security=self.instrument,
                    robot=self.robot,
                    quantity=quantity,
                    status="OPEN",
                    pnl=0.0,
                    open_price=open_price,
                    side=self.side,
                    broker_id=broker_id,
                    broker="oanda").save()

        SystemMessages(msg_type="Trade Execution",
                       msg="Open [" + str(broker_id) + "] " + self.robot + " " + str(quantity) + "@" + str(open_price)).save()

    def close_trade(self):
        return ""

    def close_all_trades(self):
        open_trades = self.get_open_trades()
        if len(open_trades) == 0:
            return None

        for id, trd in zip(open_trades["id"], open_trades["broker_id"]):
            print("Close -> OANDA ID:", trd)

            open_trade = self.connection.close_trades(trd_id=trd)

            print("Update -> Database ID:", id)

            trade_record = RobotTrades.objects.get(id=id)
            trade_record.status = "CLOSED"
            trade_record.close_price = open_trade["price"]
            trade_record.pnl = open_trade["pl"]
            trade_record.close_time = get_today()
            trade_record.save()

            SystemMessages(msg_type="Trade Execution",
                           msg="Close all trades [" + str(trd) + "] " + self.robot + " P&L: " + str(open_trade["pl"])).save()

    def run(self):
        print("Start of strategy execution")
        period = 60 * self.time_multiplier
        print("PERIOD", period)
        while True:
            sleep(1)
            # Checking robot status
            status = self.get_status()
            if status == 'inactive':
                open_trades = self.get_open_trades()
                if len(open_trades) > 0:
                    print("Closing open trades")
                break

            if int((60 * self.time_multiplier) - time() % (60 * self.time_multiplier)) == period - 5:
                # Generating Signal based on strategy
                self.add_new_row(df=self.create_dataframe(self.get_candle_data(count=1)))
                signal = self.strategy_evaluate(df=self.initial_df)

                print(self.initial_df.tail(5))

                # Pre Trade risk evaluation processes

                # Executing Trade
                self.execute_trade(signal=signal)
                print("SIGNAL:", signal)


def run_robot(robot, side):
    robot_status = Robots.objects.get(name=robot)

    if robot_status.status == "active":
        print("Robot is running")
        return "Robot is already running. End of execution"
    else:
        robot_status.status = "active"
        robot_status.save()
        RobotExecution(robot=robot, side=side).run()


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

        if side == "SELL" and float(current_price) > float(sl):
            print("SELL SL Trigger")

    pnl_info = " Total P&L:" + str(total_pnl) + " Total Return:" + str(
        total_pnl / robot_balance) + " Max Risk Loss Exposure:" + str((risk_exposure * -1) * 100)

    print(pnl_info, "SL", sl, "Price", current_price)

    # Loss treshold breached
    if (total_pnl / robot_balance) < (risk_exposure * -1):
        return "Execution stopped. Reason: Risk Controll -> Exposure treshold"


