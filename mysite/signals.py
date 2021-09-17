from robots.models import Robots, RobotTrades, Balance
from risk.models import RobotRisk
from portfolio.models import Positions

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache
from django.conf import settings
from django.db import connection
from django.core import serializers
import json


# @receiver(post_save, sender=Balance)
# @receiver(post_save, sender=RobotRisk)
# @receiver(post_save, sender=Robots)
# def load_robot_status(sender, **kwargs):
#     print("------------------------------")
#     print("SIGNAL -> Robot Info Update")
#     instance = kwargs.get('instance')
#
#     if isinstance(instance, RobotRisk):
#         print("Robot risk instance")
#         robot_name = instance.robot
#
#     if isinstance(instance, Balance):
#         print("Balance instance")
#         robot_name = instance.robot_name
#
#     if isinstance(instance, Robots):
#         print("Robots instance")
#         robot_name = instance.name
#
#     print("Robot Name:", robot_name)
#
#     base_dir = settings.BASE_DIR
#     cursor = connection.cursor()
#     cursor.execute("""select r.id, r.name, r.strategy, r.security,
#     r.broker, r.status, ri.daily_risk_perc,
#     ri.daily_trade_limit, ri.risk_per_trade, bal.close_balance, bal.date, ri.sl, ri.win_exp
#     from robots_robots as r,
#     accounts_brokeraccounts as ba,
#     risk_robotrisk as ri,
#     robots_balance as bal
#     where r.account_number=ba.account_number
#     and ri.robot = r.name
#     and bal.robot_name = ri.robot
#     and ri.robot='{robot_name}'
#     order by bal.date desc limit 1;""".format(robot_name=robot_name))
#     row = cursor.fetchall()[0]
#     print(row)
#
#     try:
#         with open(base_dir + '/cache/robots/info/' + robot_name + '_status.json', "w") as outfile:
#             json.dump({'id': row[0],
#                        'name': row[1],
#                        'status': row[5],
#                        'risk_on_trade': row[8],
#                        'balance': row[9],
#                        'sl': row[11],
#                        'win_exp': row[12]}, outfile)
#     finally:
#         pass
#
#     print("------------------------------")
#
#
# @receiver(post_save, sender=RobotTrades)
# def load_robot_trades(sender, **kwargs):
#     print("------------------------------")
#     print("SIGNAL -> Robot Trades Update")
#     robot_data = kwargs.get('instance')
#     print("ROBOT: ", robot_data.robot)
#     robot_trades = RobotTrades.objects.filter(robot=robot_data.robot).filter(status="OPEN").values()
#
#     base_dir = settings.BASE_DIR
#
#     trade_list = []
#
#     for trade in robot_trades:
#         trade_list.append({'id': trade['id'],
#                            'security': trade['security'],
#                            'quantity': trade['quantity'],
#                            'side': trade['side'],
#                            'open_price': trade['open_price'],
#                            'broker_id': trade['broker_id']})
#
#     try:
#         with open(base_dir + '/cache/robots/trades/' + robot_data.robot + '_trades.json', "w") as outfile:
#             json.dump(trade_list, outfile)
#     finally:
#         pass
#
#     print("------------------------------")
#
#
