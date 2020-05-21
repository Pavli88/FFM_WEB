from django.db import models

"Restarting migration"
"python manage.py migrate --fake robots zero"


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
    broker_id = models.IntegerField(default=0)
    broker = models.CharField(max_length=30, default="")
    sl = models.FloatField(default=0.0)


class HomePageDefault(models.Model):
    account_number = models.CharField(max_length=30, default="")


class Settings(models.Model):
    ov_status = models.BooleanField()
    ov_st_time = models.TimeField()
    ov_en_time = models.TimeField()