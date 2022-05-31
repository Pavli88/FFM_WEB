# Models
from robots.models import Robots, RobotTrades, Balance
from risk.models import RobotRisk
from portfolio.models import Positions, CashFlow, CashHolding, Trade
from instrument.models import Instruments
from django_q.models import Schedule

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache
from mysite.my_functions.general_functions import *

# Processes
from robots.processes.robot_balance_calc import *
from robots.processes.robot_pricing import pricing_robot
from portfolio.processes.cash_holding import cash_holding
from portfolio.processes.port_pos import portfolio_positions
from datetime import datetime, timedelta


@receiver(post_save, sender=RobotTrades)
def trade_closed(sender, **kwargs):
    print("------------------------------")
    print("SIGNAL -> Robot Transaction Table Updated")
    robot_data = kwargs.get('instance')
    print("ROBOT: ", robot_data.robot)
    print("BROKER ID: ", robot_data.broker_id)
    print("SIGNAL: ", robot_data.status)
    print("CLOSE TIME:", robot_data.close_time)

    if robot_data.status == "OPEN":
        SystemMessages(msg_type="Trade",
                       msg_sub_type='Open',
                       msg=str(' ').join([robot_data.robot,
                                          str(robot_data.quantity),
                                          '@',
                                          str(robot_data.open_price),
                                          ])).save()
    if robot_data.status == "CLOSED":
        # close_time = datetime.strptime(robot_data.close_time, "%Y-%m-%d").date()
        # while close_time <= get_today():
        #     print(close_time)
        #
        #     close_time=close_time+timedelta(days=1)
        balance_msg = balance_calc(robot=robot_data.robot, calc_date=get_today())
        SystemMessages(msg_type="Trade",
                       msg_sub_type='Close',
                       msg=str(' ').join([robot_data.robot,
                                          str(robot_data.quantity),
                                          '@',
                                          str(robot_data.close_price),
                                          'P&L',
                                          str(robot_data.pnl)
                                          ])).save()
        SystemMessages(msg_type="Process",
                       msg_sub_type='Balance Calculation',
                       msg=balance_msg).save()
    print("------------------------------")


@receiver(post_save, sender=Robots)
def delete_robot_execution_schedule(sender, **kwargs):
    instance = kwargs.get('instance')
    if instance.status == 'inactive':
        Schedule.objects.filter(name=instance.name).delete()


@receiver(post_save, sender=Balance)
def calculate_robot_price(sender, **kwargs):
    print("------------------------------")
    print("SIGNAL -> Balance Calculation")
    balance_data = kwargs.get('instance')
    instrument = Instruments.objects.filter(instrument_name=balance_data.robot_name).values()[0]
    print("ROBOT: ", balance_data.robot_name)
    print(instrument['id'])
    pricing_response = pricing_robot(robot=balance_data.robot_name, calc_date=balance_data.date, instrument_id=instrument['id'])
    print(pricing_response)


# Portfolio related signals
@receiver(post_save, sender=CashFlow)
def run_port_cash_holding(sender, **kwargs):
    print("--------------------------------------------")
    print("SIGNAL -> Portfolio Cash Holding Calculation")
    cash_data = kwargs.get('instance')
    print("PORTFOLIO: ", cash_data.portfolio_code)
    cash_holding_calc_response = cash_holding(portfolio=cash_data.portfolio_code, calc_date=get_today())
    print(cash_holding_calc_response)
    SystemMessages(msg_type="Process",
                   msg_sub_type='Portfolio Cash Holding',
                   msg=cash_holding_calc_response).save()


@receiver(post_save, sender=Trade)
def run_port_positions(sender, **kwargs):
    print("--------------------------------------------")
    print("SIGNAL -> Portfolio Positions Calculation")
    trade_data = kwargs.get('instance')
    print(trade_data.portfolio_name, trade_data.date)
    positions_calc_response = portfolio_positions(portfolio=trade_data.portfolio_name, calc_date=trade_data.date)
    print(positions_calc_response)
    SystemMessages(msg_type="Process",
                   msg_sub_type='Portfolio Positions',
                   msg=positions_calc_response).save()