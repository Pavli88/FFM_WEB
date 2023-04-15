from risk.models import *


def get_robot_risk_data(robot=None):
    if robot is None:
        return RobotRisk.objects.filter().values()
    elif robot is not None:
        return RobotRisk.objects.filter(robot=robot).values()