from robots.robot_functions import *


def get_open_trades(robot):
    return RobotTrades.objects.filter(robot=robot, status="OPEN").values()


def quantity_calc():
    pass


# RISK FUNCTIONS
def pyramiding_check(robot):
    pass


def daily_risk_limit_check():
    pass

