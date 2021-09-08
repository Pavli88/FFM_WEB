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


def get_robot_trades(robot, open_time=None, close_time=None):
    if close_time is not None:
        return RobotTrades.objects.filter(robot=robot, close_time=close_time).values()
    elif open_time is not None:
        return RobotTrades.objects.filter(robot=robot, open_time=open_time).values()
    else:
        return RobotTrades.objects.filter(robot=robot).values()


def get_robot_balance(robot_name, start_date=None, end_date=None):
    robot_balance = Balance.objects.filter(robot_name=robot_name).values()
    return robot_balance


def new_trade(security, robot, quantity, open_price, side, broker_id):
    RobotTrades(security=security,
                robot=robot,
                quantity=quantity,
                status="OPEN",
                pnl=0.0,
                open_price=open_price,
                side=side,
                broker_id=broker_id,
                broker="oanda").save()

