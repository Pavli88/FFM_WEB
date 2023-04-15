# General package imports
from time import time, sleep
import datetime
import os
import pandas as pd
import logging
import json
import requests
#import matplotlib.pyplot as plt
import importlib

from mysite.my_functions.general_functions import *

# Database imports
from mysite.models import *
from robots.models import *
from risk.models import *
from robots.models import *
from accounts.models import BrokerAccounts
from signals.models import Strategies

# Django imports
from django.conf import settings

# Process imports
from mysite.processes.oanda import *


class RobotExecution:
    def __init__(self, robot, time_frame,
                 strategy, instrument, broker,
                 env, account_number, token, strategy_location, params):
        self.robot = robot
        self.strategy = strategy
        self.instrument = instrument
        self.broker = broker
        self.environment = env
        self.account_number = account_number
        self.token = token
        self.time_frame = time_frame
        self.side = params['side']
        self.url = 'https://pavliati.pythonanywhere.com/' # 'https://pavliati.pythonanywhere.com/'  'http://127.0.0.1:8000/'

        # this goes to a variable and loaded from db
        self.strategy_location = importlib.import_module(strategy_location)
        self.strategy_evaluate = getattr(self.strategy_location, "strategy_evaluate")
        self.params = params['strategy_params']

        # Setting up broker connection
        # This part has to be loaded with importlib as well in the future to create connection function
        self.connection = OandaV20(access_token=self.token,
                                   account_id=self.account_number,
                                   environment=self.environment)

        # Requesting initial candle data from broker
        candle_data = self.connection.candle_data(instrument=self.instrument,
                                                  count=500,
                                                  time_frame=self.time_frame)['candles']

        # Setting up initial dataframe
        self.initial_df = self.create_dataframe(data=candle_data)

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

    def run(self):
        sleep(5)
        signal = self.strategy_evaluate(df=self.initial_df, params=self.params)
        # print(self.time_frame, self.robot, self.side, 'Signal:', signal, 'Strategy Params:', self.params)

        # logging.basicConfig(format='%(asctime)s %(message)s',
        #                     datefmt='%m/%d/%Y %I:%M:%S %p',
        #                     filename=settings.BASE_DIR + '/process_logs/schedules/' + self.robot + '.log',
        #                     level=logging.INFO)
        # logging.info(str(' ').join(['ROBOT:', self.robot,
        #                             '- TIMEFRAME:', str(self.time_frame),
        #                             '- STRATEGY PARAMETERS:', str(self.params),
        #                             '---> | SIDE:', self.side,
        #                             '- SIGNAL:', str(signal),
        #                             '|']))
        # print(self.initial_df.tail(30))

        # plt.figure(figsize=[15, 10])
        # plt.grid(True)
        # plt.plot(self.initial_df['MA10(close_to_MA50(close))'], label='data')
        # plt.plot(self.initial_df['MA100(close_to_MA100(close))'], label='SMA 3 Months')
        # plt.plot(self.initial_df['close_to_MA200(close)'], label='SMA 4 Months')
        # plt.plot(self.initial_df['close_to_MA50(close)'], label='SMA 4 Months')
        # plt.legend(loc=2)
        # plt.axhline(y=self.params['threshold'], color='r', linestyle='-')
        # plt.savefig('/home/pavlicseka/Documents/' + self.robot + self.time_frame + '.png')
        # plt.close()

        #     if int((60 * self.time_multiplier) - time() % (60 * self.time_multiplier)) == period - 10:


def run_robot(robot):
    robot_status = Robots.objects.get(name=robot)
    robot_status.status = 'active'
    robot_status.save()
    account_data = BrokerAccounts.objects.get(account_number=robot_status.account_number)
    strategy = Strategies.objects.get(name=robot_status.strategy)
    RobotExecution(robot=robot,
                   time_frame=robot_status.time_frame,
                   strategy=robot_status.strategy,
                   instrument=robot_status.security,
                   broker=robot_status.broker,
                   env=robot_status.env,
                   account_number=robot_status.account_number,
                   token=account_data.access_token,
                   strategy_location=strategy.location,
                   params=robot_status.strategy_params).run()

    return "Interrupted." + robot

