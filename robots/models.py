from django.db import models

"Restarting migration"
"python manage.py migrate --fake robots zero"


class Robots(models.Model):
    name = models.CharField(max_length=20, unique=True)
    strategy = models.CharField(max_length=50, default='')
    security = models.CharField(max_length=50, default='')
    broker = models.CharField(max_length=50, default='')
    status = models.CharField(max_length=50, default='')
    env = models.CharField(max_length=50, default='')
    pyramiding_level = models.FloatField(default=0.0)
    in_exp = models.FloatField(default=0.0)
    quantity = models.FloatField(default=0.0)
    time_frame = models.CharField(max_length=50, default='')
    account_number = models.CharField(max_length=50, default='')
    sl_policy = models.CharField(max_length=50, default='')
    prec = models.IntegerField(default=1)


class RobotCashFlow(models.Model):
    robot_name = models.CharField(max_length=20)
    cash_flow = models.FloatField(default=0.0)
    date = models.DateTimeField(auto_now=True)


class Balance(models.Model):
    robot_name = models.CharField(max_length=20)
    daily_pnl = models.FloatField(default=0.0)
    daily_cash_flow = models.FloatField(default=0.0)
    balance = models.FloatField(default=0.0)
    date = models.DateTimeField(auto_now=True)





