from django.db import connection
from django_q.tasks import AsyncTask, Task

from mysite.processes.oanda import *
from mysite.my_functions.general_functions import *

# Database imports
from robots.models import RobotTrades


def close_trade_task(robot, broker_id):
    # Executing task at message broker queue
    task = AsyncTask(close_trade_by_broker_id,
                     task_name="trade_close_" + robot + "_" + str(broker_id),
                     timeout=100)
    task.args = (robot, broker_id)
    task.run()


def trade_close_hook(task):
    print("TRADE CLOSE TASK HOOK")
    print(task.result)
    print(task.id)


def close_trade_by_broker_id(robot, broker_id):
    # Loading data from database
    cursor = connection.cursor()
    cursor.execute("""select r.name, r.broker, r.env, r.account_number, 
                        rt.id, rt.broker_id, ac.access_token, rt.status
                        from robots_robots as r,
                        robots_robottrades as rt,
                        accounts_brokeraccounts as ac
                        where r.name=rt.robot
                        and r.account_number=ac.account_number
                        and rt.status='OPEN'
                        and r.name='{robot}'
                        and rt.broker_id={broker_id};""".format(robot=robot, broker_id=broker_id))

    row = cursor.fetchall()[0]

    print(row)

    if row[2] == 'demo':
        env = 'practice'
    else:
        env = 'live'

    open_trade = OandaV20(access_token=row[6], account_id=row[3], environment=env).close_trades(trd_id=row[5])
    print(open_trade)
    print("Update -> Database ID:", row[4])

    trade_record = RobotTrades.objects.get(id=row[4])
    trade_record.status = "CLOSED"
    trade_record.close_price = open_trade["price"]
    trade_record.pnl = open_trade["pl"]
    trade_record.close_time = get_today()
    trade_record.save()
    #
    # SystemMessages(msg_type="Trade Execution",
    #                msg="CLOSE: " + robot + " - P&L - " + str(open_trade["pl"])).save()

    return ""