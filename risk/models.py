from django.db import models


class AccountRisk(models.Model):
    account = models.CharField(max_length=50, default="")
    daily_risk_limit = models.FloatField(default=0.00)
