from robots.models import Robots
from portfolio.models import Positions

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache
from django.conf import settings

import json


@receiver(post_save, sender=Robots)
def update_robot_data(sender, **kwargs):
    print("SIGNAL: Update Table -> Robots")
    base_dir = settings.BASE_DIR
    robots = Robots.objects.filter().values()

    robot_dict = {}
    for robot in robots:
        a = robot['name']
        try:
            robot_dict[a] = robot['status']
        finally:
            pass

    with open(base_dir + '/process_logs/robot_status.json', "w") as outfile:
        json.dump(robot_dict, outfile)


