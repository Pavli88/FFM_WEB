from django.db import models


class Portfolio(models.Model):
    portfolio_name = models.CharField(max_length=30, default="", unique=True)
    portfolio_type = models.CharField(max_length=30, default="")
    status = models.CharField(max_length=30, default="")
    currency = models.CharField(max_length=30, default="")
    inception_date = models.DateTimeField(auto_now=True)


class CashFlow(models.Model):
    portfolio_name = models.CharField(max_length=30, default="")
    amount = models.FloatField(default=0.0)
    type = models.CharField(max_length=30, default="")
    user = models.CharField(max_length=30, default="")
    date = models.DateTimeField(auto_now=True)


class Nav(models.Model):
    portfolio_name = models.CharField(max_length=30, default="")
    amount = models.FloatField(default=0.0)
    date = models.DateTimeField(auto_now=True)


class Trade(models.Model):
    portfolio_name = models.CharField(max_length=30, default="")
    security = models.IntegerField(default=0)
    sec_type = models.CharField(max_length=30, default="")
    quantity = models.FloatField(default=0.0)
    price = models.FloatField(default=0.0)
    mv = models.FloatField(default=0.0)
    source = models.CharField(max_length=30, default="")
    date = models.DateField(auto_now=True)


class Positions(models.Model):
    portfolio_name = models.CharField(max_length=30, default="")
    security = models.IntegerField(default=0)
    quantity = models.FloatField(default=0.0)
    date = models.DateField()