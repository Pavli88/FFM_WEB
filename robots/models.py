from django.db import models
import datetime

"Restarting migration"
"python manage.py migrate --fake robots zero"


class Robots(models.Model):
    name = models.CharField(max_length=30, unique=True)
    color = models.CharField(max_length=20, default='#828282')
    strategy_id = models.CharField(max_length=50, default='')
    security = models.CharField(max_length=50, default='')
    broker = models.CharField(max_length=50, default='')
    status = models.CharField(max_length=50, default='')
    env = models.CharField(max_length=50, default='')
    time_frame = models.CharField(max_length=50, default='')
    account_number = models.CharField(max_length=50, default='')
    inception_date = models.DateField(default=datetime.date.today)
    currency = models.CharField(max_length=50, default='')


class Strategy(models.Model):
    name = models.CharField(max_length=50, unique=True)
    type = models.CharField(max_length=50, unique=True)


class RobotCashFlow(models.Model):
    robot_name = models.CharField(max_length=20)
    cash_flow = models.FloatField(default=0.0)
    date = models.DateField(default=datetime.date.today)


class Balance(models.Model):
    robot_id = models.IntegerField(default=0)
    opening_balance = models.FloatField(default=0.0)
    realized_pnl = models.FloatField(default=0.0)
    unrealized_pnl = models.FloatField(default=0.0)
    cash_flow = models.FloatField(default=0.0)
    close_balance = models.FloatField(default=0.0)
    ret = models.FloatField(default=0.0)
    date = models.DateField(default=datetime.date.today)


class RobotTrades(models.Model):
    security = models.CharField(max_length=30, default="")
    robot = models.CharField(max_length=30, default="")
    quantity = models.FloatField(default=0.0)
    status = models.CharField(max_length=30, default="")
    pnl = models.FloatField(default=0.0)
    open_price = models.FloatField(default=0.0)
    close_price = models.FloatField(default=0.0)
    open_time = models.DateField(auto_now_add=True)
    close_time = models.DateField(auto_now_add=True)
    side = models.CharField(max_length=30, default="")
    broker_id = models.IntegerField(default=0)
    broker = models.CharField(max_length=30, default="")
    sl = models.FloatField(default=0.0)


class MonthlyReturns(models.Model):
    robot_id = models.IntegerField(default=0)
    ret = models.FloatField(default=0.0)
    date = models.DateField(default=datetime.date.today)



