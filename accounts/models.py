from django.db import models


class BrokerAccounts(models.Model):
    broker_name = models.CharField(max_length=30, default="")
    account_name = models.CharField(max_length=30, default="")
    account_number = models.CharField(max_length=50, default="", unique=True)
    access_token = models.CharField(max_length=100, default="")
    env = models.CharField(max_length=100, default="")
    currency = models.CharField(max_length=100, default="")


class AccountBalance(models.Model):
    account_number = models.CharField(max_length=50, default="")
    allocated = models.FloatField(default=0.0)
    not_allocated = models.FloatField(default=0.0)
    currency = models.CharField(max_length=100, default="")
    models.DateField(auto_now=True)


class AccountCashFlow(models.Model):
    account_number = models.CharField(max_length=50, default="")
    cash_flow = models.FloatField(default=0.0)
    currency = models.CharField(max_length=100, default="")
    date = models.DateField(auto_now=True)


class Brokers(models.Model):
    broker = models.CharField(max_length=50, default="")
    broker_code = models.CharField(max_length=50, default="", unique=True)
