from django.db import models
from django.contrib.auth.models import User

class BrokerAccounts(models.Model):
    broker_name = models.CharField(max_length=30, default="")
    account_name = models.CharField(max_length=30, default="")
    account_number = models.CharField(max_length=50, default="")
    access_token = models.CharField(max_length=100, default="")
    env = models.CharField(max_length=100, default="")
    currency = models.CharField(max_length=100, default="")
    owner = models.CharField(max_length=30, default="")
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column="user", null=True, blank=True, default=None)
    margin_account = models.BooleanField(default=False)
    margin_percentage = models.FloatField(default=0.0)

class Brokers(models.Model):
    broker = models.CharField(max_length=50, default="")
    broker_code = models.CharField(max_length=50, default="", unique=True)
