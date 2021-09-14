from django.apps import AppConfig
from django.core.cache import cache
from django.core import serializers
from django.conf import settings
import json


class MySiteConfig(AppConfig):
    name = 'mysite'

    def ready(self):
        print("Main application is ready to load initial processes")
        base_dir = settings.BASE_DIR
        from robots.models import Robots

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




        # with open(base_dir + '/process_logs/cache_2.json', "w") as out:
        #     mast_point = serializers.serialize("json", robots)
        #     out.write(mast_point)

        # for robot in robots:
        #     cache.set(robot['name'], robot)

        # Post save signals on models
        import mysite.signals
