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

        # Initial robot info load to files
        # robots = Robots.objects.filter().values()
        # robot_dict = {}
        #
        # for robot in robots:
        #     robot_name = robot['name']
        #     try:
        #         with open(base_dir + '/cache/robots/info/' + robot_name + '_status.json', "w") as outfile:
        #             robot_dict[robot_name] = robot['status']
        #             json.dump(robot_dict, outfile)
        #     finally:
        #         pass

        # Initial open trades load to files






        # with open(base_dir + '/process_logs/cache_2.json', "w") as out:
        #     mast_point = serializers.serialize("json", robots)
        #     out.write(mast_point)

        # for robot in robots:
        #     cache.set(robot['name'], robot)

        # Post save signals on models
        import mysite.signals
