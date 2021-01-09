from django.db import models


class AccountRisk(models.Model):
    account = models.CharField(max_length=50, default="")
    daily_risk_limit = models.FloatField(default=0.00)


class RobotRisk(models.Model):
    robot = models.CharField(max_length=50, unique=True, default="")
    daily_risk_perc = models.FloatField(default=0.00)
    daily_trade_limit = models.FloatField(default=0.00)
