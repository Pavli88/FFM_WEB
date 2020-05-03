from django.db import models

"Restarting migration"
"python manage.py migrate --fake robots zero"


class BrokerAccounts(models.Model):
    broker_name = models.CharField(max_length=30, default="")
    account_number = models.CharField(max_length=50, default="")
    access_token = models.CharField(max_length=100, default="")
    env = models.CharField(max_length=100, default="")


class Trades(models.Model):
    security = models.CharField(max_length=30, default="")
    robot = models.CharField(max_length=30, default="")
    quantity = models.FloatField(default=0.0)
    strategy = models.CharField(max_length=30, default="")
    status = models.CharField(max_length=30, default="")
    pnl = models.FloatField(default=0.0)
    open_price = models.FloatField(default=0.0)
    close_price = models.FloatField(default=0.0)
    open_time = models.DateTimeField(auto_now_add=True)
    close_time = models.DateTimeField(auto_now=True)
    time_frame = models.CharField(max_length=30, default="")
    side = models.CharField(max_length=30, default="")