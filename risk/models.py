from django.db import models


class AccountRisk(models.Model):
    account = models.CharField(max_length=50, default="")
    daily_risk_limit = models.FloatField(default=0.00)


class RobotRisk(models.Model):
    robot = models.CharField(max_length=50, default="")
    p_level = models.IntegerField(default=0)
    in_exp = models.FloatField(default=0.00)
    sl_policy = models.CharField(max_length=20, default="")
    quantity = models.IntegerField(default=0)
