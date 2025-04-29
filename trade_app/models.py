from django.db import models
from portfolio.models import Portfolio
from accounts.models import Brokers

class Notifications(models.Model):
    portfolio_code = models.CharField(max_length=50, default="")
    message = models.CharField(max_length=50, default="")
    sub_message = models.CharField(max_length=50, default="")
    security = models.CharField(max_length=50, default="")
    broker_name = models.CharField(max_length=50, default="")
    date = models.DateField(auto_now=True)
    time = models.DateTimeField(auto_now=True)


class Orders(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, null=True, blank=True, default=None)
    broker = models.ForeignKey(Brokers, on_delete=models.CASCADE, null=True, blank=True, default=None)
    status = models.CharField(max_length=30, default="")