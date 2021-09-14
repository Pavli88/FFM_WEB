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

    # Create and configure logger
    # logging.basicConfig(filename=base_dir + "/process_logs/robot_executions/" + robot + "_" + datetime.datetime.now().strftime("%m_%d_%Y_%H_%M") + ".log",
    #                     format='%(asctime)s %(message)s',
    #                     filemode='w')
    # logger = logging.getLogger()
    # logger.setLevel(logging.INFO)

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
        # logger.info("Execution stopped. Robot is already running")
        return "Execution stopped. Robot is already running"

    # Updating robot status to active
    robot_status = Robots.objects.get(name=robot)
    robot_status.status = 'active'
    robot_status.save()

    with open(base_dir + '/cache/robots/info/' + robot + '_status.json', "w") as outfile:
        json.dump({robot: 'active'}, outfile)

    # logger.info("NEW ROBOT EXUECUTION PROCESS")
    # logger.info("BASE DIR: " + str(base_dir))
    # logger.info("Creating oanda instance")
    # logger.info("ACCESS TOKEN: " + str(row[8]))
    # logger.info("ACCOUNT ID: " + str(row[7]))
    # logger.info("ENV: " +  str(row[6]))
    # logger.info("SECURITY: " + str(row[3]))

    # Fetching open trades for robot
    robot_balance = Balance.objects.filter(robot_name=robot).order_by('-id')[0].close_balance

    # Creating broker connection instance for the price streaming
    oanda_api = OandaV20(access_token=row[8],
                         account_id=row[7],
                         environment=row[6]).pricing_stream(instrument=row[3])

    # Running trade and risk live evaluation
    for ticks in oanda_api:
        # Requesting robot data from cache
        # This part is responsible for allowing the robot either run in the task qouee or not. It is based on
        # the robot status
        try:
            # Loading robot status, risk and balance parameters
            with open(base_dir + '/cache/robots/info/' + robot + '_status.json') as json_file:
                data = json.load(json_file)
        except:
            # logger.info("Execution stopped. Error during cache file data load")
            return "Execution stopped. Error during cache file data load"

        if data[robot] == "inactive":
            # logger.info("Execution stopped. Inactive robot status")
            return "Execution stopped. Inactive robot status"

        # Try to fetch price from broker
        try:
            if ticks['type'] == 'PRICE':
                prices = {'bid': ticks['bids'][0]['price'],
                          'ask': ticks['asks'][0]['price']}
                mid_price = (float(prices['bid']) + float(prices['ask'])) / 2
        except:
            # logger.info("Error occured during streaming. Connection lost")
            return "Error occured during streaming. Connection lost"

        # Evaluation open trades based on risk parameters
        with open(base_dir + '/cache/robots/trades/' + robot + '_trades.json') as json_file:
            trades_data = json.load(json_file)

        total_pnl = 0.0
        for trade in trades_data:
            print(trade)
            side = trade['side']
            quantity = trade['quantity']
            open_price = trade['open_price']

            if side == "SELL":
                pnl = ((quantity * open_price) - (quantity * mid_price)) * -1
            if side == "BUY":
                pnl = (quantity * mid_price) - (quantity * open_price)
            total_pnl = + total_pnl + pnl

        pnl_info = " Total P&L:" + str(total_pnl) + " Total Return:" + str(
            total_pnl / robot_balance) + " Max Risk Loss Exposure:" + str((risk_exposure * -1) * 100)
        print(pnl_info)

        if (total_pnl / robot_balance) < (risk_exposure * -1):
            # logger.info("Execution stopped. Reason: Risk Controll -> Exposure")
            return "Execution stopped. Reason: Risk Controll -> Exposure treshold"


    return "End of task"
