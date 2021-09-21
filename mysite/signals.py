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
@receiver(post_save, sender=Robots)
def load_robot_status(sender, **kwargs):
    print("------------------------------")
    print("SIGNAL -> Robot Info Update")
    instance = kwargs.get('instance')
    print("Loading data to cache")
    cache.set(instance.name, instance.status, 30)
    print("Robot Name - ", instance.name)
    print("Robot Status - ", instance.status)

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
