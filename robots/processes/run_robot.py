# General package imports
import time
import datetime
import os
import pandas as pd
import logging
import json

# Database imports
from mysite.models import *
from robots.models import *

# Django imports
from django.db import connection
from robots.models import *
from django.conf import settings
from django.core.cache import cache
from django.db.models.signals import post_save
from django.dispatch import receiver

# Process imports
from mysite.processes.oanda import *


def run_robot(robot):
    base_dir = settings.BASE_DIR

    # Fetching robot info from database
    cursor = connection.cursor()
    cursor.execute("""select r.id, r.name, r.strategy, r.security,
                            r.broker, r.status, r.env, r.account_number,
                            ba.access_token, ri.quantity, ri.quantity_type, 
                            ri.daily_risk_perc,ri.daily_trade_limit, ri.risk_per_trade
                        from robots_robots as r, accounts_brokeraccounts as ba, risk_robotrisk as ri
                        where r.account_number=ba.account_number
                        and r.name='{robot}' and ri.robot = r.name;""".format(robot=robot))
    row = cursor.fetchall()[0]
    risk_exposure = row[13]

    # Checking if robot is already running
    if row[5] == 'active':
        return "Execution stopped. Robot is already running"

    # Updating robot status to active
    robot_status = Robots.objects.get(name=robot)
    robot_status.status = 'active'
    robot_status.save()
    with open(base_dir + '/cache/robots/info/' + robot + '_status.json', "w") as outfile:
        json.dump({robot: 'active'}, outfile)

    # Fetching open trades for robot
    robot_balance = Balance.objects.filter(robot_name=robot).order_by('-id')[0].close_balance

    # Creating broker connection instance for the price streaming
    oanda_api = OandaV20(access_token=row[8],
                         account_id=row[7],
                         environment=row[6]).pricing_stream(instrument=row[3])

    # Running trade and risk live evaluation
    for ticks in oanda_api:

        # FETCHING DATA FROM CACHE--------------------------------------------------------------------------------------
        # Fetching robot status
        try:
            # Loading robot status, risk and balance parameters
            with open(base_dir + '/cache/robots/info/' + robot + '_status.json') as json_file:
                data = json.load(json_file)
        except:
            return "Execution stopped. Error during cache file data load"

        if data[robot] == "inactive":
            return "Execution stopped. Inactive robot status"

        # Fetching open trades
        with open(base_dir + '/cache/robots/trades/' + robot + '_trades.json') as json_file:
            trades_data = json.load(json_file)

        # --------------------------------------------------------------------------------------------------------------

        # Try to fetch price from broker
        try:
            if ticks['type'] == 'PRICE':
                prices = {'bid': ticks['bids'][0]['price'],
                          'ask': ticks['asks'][0]['price']}
                mid_price = (float(prices['bid']) + float(prices['ask'])) / 2
        except:
            return "Error occured during streaming. Connection lost"

        # Risk controll
        risk_control(trades_data=trades_data, current_price=mid_price, robot_balance=robot_balance, risk_exposure=risk_exposure)

    return "End of task"


def risk_control(trades_data, current_price, robot_balance, risk_exposure):
    total_pnl = 0.0
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

    pnl_info = " Total P&L:" + str(total_pnl) + " Total Return:" + str(
        total_pnl / robot_balance) + " Max Risk Loss Exposure:" + str((risk_exposure * -1) * 100)
    print(pnl_info)

    # Loss treshold breached
    if (total_pnl / robot_balance) < (risk_exposure * -1):
        return "Execution stopped. Reason: Risk Controll -> Exposure treshold"
