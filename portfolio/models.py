from django.db import models


class Portfolio(models.Model):
    portfolio_name = models.CharField(max_length=30, default="", unique=True)
    portfolio_type = models.CharField(max_length=30, default="")


class CashFlow(models.Model):
    portfolio_name = models.CharField(max_length=30, default="")
    amount = models.FloatField(default=0.0)
    type = models.CharField(max_length=30, default="")
    date = models.DateTimeField(auto_now=True)


class Nav(models.Model):
    portfolio_name = models.CharField(max_length=30, default="")
    amount = models.FloatField(default=0.0)
    date = models.DateTimeField(auto_now=True)


class Trade(models.Model):
    portfolio_name = models.CharField(max_length=30, default="")
    quantity = models.FloatField(default=0.0)
    price = models.FloatField(default=0.0)
    mv = models.FloatField(default=0.0)
    date = models.DateTimeField(auto_now=True)


class Instruments(models.Model):
    instrument_name = models.CharField(max_length=30, default="")
    instrument_type = models.CharField(max_length=30, default="")
    source = models.CharField(max_length=30, default="")