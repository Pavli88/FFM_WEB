# General package imports
import time
import datetime
import os
import pandas as pd
import logging

# Database imports
from mysite.models import *
from robots.models import *

# Django imports
from django.db import connection
from robots.models import *
from django.conf import settings

# Process imports
from mysite.processes.oanda import *


def run_robot(robot):
    base_dir = settings.BASE_DIR

    # Create and configure logger
    logging.basicConfig(filename=base_dir + "/process_logs/robot_runs/" + robot + "_" + datetime.datetime.now().strftime("%m_%d_%Y_%H_%M") + ".log",
                        format='%(asctime)s %(message)s',
                        filemode='w')
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

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
    print(row)

    risk_exposure = row[13]
    print(risk_exposure)
    logger.info("NEW ROBOT EXUECUTION PROCESS")
    logger.info("BASE DIR: " + str(base_dir))
    logger.info("Creating oanda instance")
    logger.info("ACCESS TOKEN: " + str(row[8]))
    logger.info("ACCOUNT ID: " + str(row[7]))
    logger.info("ENV: " +  str(row[6]))
    logger.info("SECURITY: " + str(row[3]))

    # Fetching open trades for robot
    trades = pd.DataFrame(RobotTrades.objects.filter(robot=robot).filter(status="OPEN").values())

    if len(trades) == 0:
        logger.info("Execution stopped. Reason: Position Cntroll -> No open trades")
        return "Execution stopped. Reason: Position COntroll -> No open trades"

    robot_balance = Balance.objects.filter(robot_name=robot).order_by('-id')[0].close_balance

    # Creating broker connection instance
    oanda_api = OandaV20(access_token=row[8],
                         account_id=row[7],
                         environment=row[6]).pricing_stream(instrument=row[3])

    # Running trade and risk live evaluation
    for ticks in oanda_api:
        robot_status = Robots.objects.get(name=robot)
        print(robot_status.status)
        if robot_status.status == "inactive":
            logger.info("Execution stopped. Inactive robot status")
            return "Execution stopped. Inactive robot status"
        try:
            if ticks['type'] == 'PRICE':
                prices = {'bid': ticks['bids'][0]['price'],
                          'ask': ticks['asks'][0]['price']}

                mid_price = (float(prices['bid']) + float(prices['ask'])) / 2
                total_pnl = 0.0

                for index, row in trades.iterrows():
                    side = row['side']
                    quantity = row['quantity']
                    open_price = row['open_price']
                    if side == "SELL":
                        pnl = ((quantity * open_price) - (quantity * mid_price)) * -1
                    if side == "BUY":
                        pnl = (quantity * mid_price) - (quantity * open_price)
                    total_pnl = + total_pnl + pnl

                pnl_info = " Total P&L:" + str(total_pnl) + " Total Return:" + str(
                    total_pnl / robot_balance) + " Max Risk Loss Exposure:" + str((risk_exposure * -1)*100)
                print(pnl_info)

                if (total_pnl / robot_balance) < (risk_exposure * -1):
                    logger.info("Execution stopped. Reason: Risk Controll -> Exposure")
                    return "Execution stopped. Reason: Risk Controll -> Exposure treshold"
        except:
            logger.info("Error occured during streaming. Connection lost")
            return "Error occured during streaming. Connection lost"

    return "End of task"