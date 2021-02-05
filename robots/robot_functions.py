from robots.models import *


def get_robots(status=None, name=None):

    """
    Queries out all robots from database and passes it back to the html
    :param request:
    :return:
    """

    if status is not None:
        return Robots.objects.filter(status=status).values()
    elif name is not None:
        return Robots.objects.filter(name=name).values()
    else:
        return Robots.objects.filter().values()


def get_robot_trades(robot, start_date=None, end_date=None, date=None):
    if date is not None:
        return RobotTrades.objects.filter(robot=robot, date=date).values()
    else:
        return RobotTrades.objects.filter(robot=robot).values()


def get_robot_balance(robot_name, start_date=None, end_date=None):
    robot_balance = Balance.objects.filter(robot_name=robot_name).values()
    return robot_balance

