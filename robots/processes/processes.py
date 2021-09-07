# General package imports
import time
import datetime
import os

# Database imports
from mysite.models import *
from robots.models import *

# Django imports
from django.db import connection

# Process imports
from mysite.processes.oanda import *


def run_robot(robot):
    print("Running robot:", robot)
    pid = os.getpid()
    print("PROCESS ID:", pid)
    robot_data = Robots.objects.filter(name=robot).values()

    # Fetching robot info from database
    cursor = connection.cursor()
    cursor.execute("""select r.id, r.name, r.strategy, r.security,
                            r.broker, r.status, r.env, r.account_number,
                            ba.access_token
                        from robots_robots as r, accounts_brokeraccounts as ba
                        where r.account_number=ba.account_number
                        and r.name='{robot}';""".format(robot=robot))
    row = cursor.fetchall()[0]

    print(row)
    print("Creating oanda instance")
    print("ACCESS TOKEN:", row[8])
    print("ACCOUNT ID:", row[7])
    print("ENV:", row[6])
    print("SECURITY:", row[3])
    oanda_api = OandaV20(access_token=row[8],
                                  account_id=row[7],
                                  environment=row[6]).pricing_stream(instrument=row[3])

    for ticks in oanda_api:
        try:
            prices = {'bid' : ticks['bids'][0]['price'],
                      'ask' : ticks['asks'][0]['price']}
            print(prices)
        except:
            pass
    # Updating process info table
    print("Updating process info table")
    process = ProcessInfo.objects.get(pid=pid, is_done=0)
    process.is_done = 1
    process.end_date = datetime.datetime.now()
    process.msg = "Succesfull Execution"
    process.save()

    return ""