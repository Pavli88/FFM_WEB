# General package imports
from time import time, sleep
import datetime
import os
import pandas as pd
import logging
import json
import matplotlib.pyplot as plt
import importlib

from mysite.my_functions.general_functions import *

# Database imports
from mysite.models import *
from robots.models import *
from risk.models import *
from robots.models import *
from accounts.models import BrokerAccounts

# Django imports
from django.db import connections
from django.db.utils import DEFAULT_DB_ALIAS, load_backend
from django.core.cache import cache

# Process imports
from mysite.processes.oanda import *


def create_db_connection(alias=DEFAULT_DB_ALIAS):
    connections.ensure_defaults(alias)
    connections.prepare_test_settings(alias)
    db = connections.databases[alias]
    backend = load_backend(db['ENGINE'])
    return backend.DatabaseWrapper(db, alias)


class RobotExecution:
    def __init__(self, robot, side, time_frame, strategy, instrument, broker, status, env, account_number, token):
        self.robot = robot
        self.strategy = strategy
        self.instrument = instrument
        self.broker = broker
        self.status = status
        self.environment = env
        self.account_number = account_number
        self.token = token
        self.time_frame = time_frame
        self.side = side

        print("")
        print("ROBOT EXECUTION")
        print("Robot:", self.robot)
        print("Strategy:", self.strategy)
        print("Instrument:", self.instrument)
        print('Side:', self.side)

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
        conn = create_db_connection()
        robot_risk = RobotRisk.objects.filter(robot=self.robot).values()[0]
        conn.close()
        return robot_risk

    def get_open_trades(self):
        conn = create_db_connection()
        open_trades = pd.DataFrame(RobotTrades.objects.filter(robot=self.robot).filter(status="OPEN").values())
        conn.close()
        return open_trades

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
                SystemMessages(msg_type="Trade",
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

        SystemMessages(msg_type="Trade",
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

            SystemMessages(msg_type="Trade",
                           msg="Close all trades [" + str(trd) + "] " + self.robot + " P&L: " + str(open_trade["pl"])).save()

    def plot_chart(self):
        plt.figure(figsize=[15, 10])
        plt.grid(True)
        plt.plot(self.initial_df['MA100_DIST100'], label='data')
        plt.plot(self.initial_df['Dist200'], label='SMA 3 Months')
        plt.plot(self.initial_df['Dist100'], label='SMA 4 Months')
        plt.legend(loc=2)
        # plt.savefig('/home/pavlicseka/Documents/test.png')
        plt.show()

    def run(self):
        print("Start of strategy execution")
        period = 60 * self.time_multiplier
        print("PERIOD", period)

        while True:
            sleep(1)
            # Checking robot status
            status = self.get_status()
            if status == 'inactive':
                # open_trades = self.get_open_trades()
                # if len(open_trades) > 0:
                #     print("Closing open trades")
                break

            if int((60 * self.time_multiplier) - time() % (60 * self.time_multiplier)) == period - 10:
                # Generating Signal based on strategy
                new_candles = self.create_dataframe(self.get_candle_data(count=1))
                print(new_candles)
                self.add_new_row(df=new_candles)
                signal = self.strategy_evaluate(df=self.initial_df)

                print(self.initial_df.tail(5))
                # Pre Trade risk evaluation processes

                # Executing Trade
                self.execute_trade(signal=signal)
                print("SIGNAL:", signal)


def run_robot(robot, side):
    robot_status = Robots.objects.get(name=robot)
    account_data = BrokerAccounts.objects.get(account_number=robot_status.account_number)

    if robot_status.status == "active":
        return "Timeout." + robot
    else:
        robot_status.status = "active"
        robot_status.save()

        RobotExecution(robot=robot,
                       side=side,
                       time_frame=robot_status.time_frame,
                       strategy=robot_status.strategy,
                       instrument=robot_status.security,
                       broker=robot_status.broker,
                       status='active',
                       env=robot_status.env,
                       account_number=robot_status.account_number,
                       token=account_data.access_token).run()
        return "Interrupted." + robot


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


