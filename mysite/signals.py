from robots.models import Robots, RobotTrades, Balance
from risk.models import RobotRisk
from portfolio.models import Positions

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache
from mysite.my_functions.general_functions import *

from robots.processes.robot_balance_calc import *


@receiver(post_save, sender=Robots)
def load_robot_status(sender, **kwargs):
    print("------------------------------")
    print("SIGNAL -> Robot Info Update")
    instance = kwargs.get('instance')
    print("Loading data to cache")
    cache.set(instance.name, instance.status, 30)
    print("Robot Name - ", instance.name)
    print("Robot Status - ", instance.status)


@receiver(post_save, sender=RobotTrades)
def trade_closed(sender, **kwargs):
    print("------------------------------")
    print("SIGNAL -> Robot Trades Closed")
    robot_data = kwargs.get('instance')
    print("ROBOT: ", robot_data.robot)
    print("BROKER ID: ", robot_data.broker_id)
    print("STATUS: ", robot_data.status)

    if robot_data.status == "CLOSED":
        balance_msg = balance_calc(robot=robot_data.robot, calc_date=get_today())
        SystemMessages(msg_type="Process",
                       msg="Robot Balance Calculation: " + balance_msg).save()
    print("------------------------------")
#
#