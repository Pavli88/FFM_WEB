from django.db import models


class Portfolio(models.Model):
    portfolio_name = models.CharField(max_length=30, default="")
    portfolio_code = models.CharField(max_length=30, unique=True)
    portfolio_type = models.CharField(max_length=30, default="")
    status = models.CharField(max_length=30, default="")
    currency = models.CharField(max_length=30, default="")
    inception_date = models.DateField(auto_now=True)


class CashFlow(models.Model):
    portfolio_code = models.CharField(max_length=30, default="")
    amount = models.FloatField(default=0.0)
    type = models.CharField(max_length=30, default="")
    user = models.CharField(max_length=30, default="")
    currency = models.CharField(max_length=30, default="")
    date = models.DateField(auto_now=True)


class CashHolding(models.Model):
    portfolio_code = models.CharField(max_length=30, default="")
    amount = models.FloatField(default=0.0)
    currency = models.CharField(max_length=30, default="")
    date = models.DateField()


class Nav(models.Model):
    portfolio_name = models.CharField(max_length=30, default="")
    portfolio_code = models.CharField(max_length=30, default="")
    pos_val = models.FloatField(default=0.0)
    cash_val = models.FloatField(default=0.0)
    accured_income = models.FloatField(default=0.0)
    short_liab = models.FloatField(default=0.0)
    long_liab = models.FloatField(default=0.0)
    accured_expenses = models.FloatField(default=0.0)
    total = models.FloatField(default=0.0)
    units = models.FloatField(default=0.0)
    nav_per_share = models.FloatField(default=0.0)
    date = models.DateField(auto_now=True)


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


class PortGroup(models.Model):
    parent_id = models.IntegerField()
    children_id = models.IntegerField()
    connection_id = models.CharField(max_length=30, default="", unique=True)


class PortfolioHoldings(models.Model):
    portfolio_code = models.CharField(max_length=30, unique=True)
    portfolio_name = models.CharField(max_length=30, default="")
    date = models.DateField()
    security = models.IntegerField(default=0)
    quantity = models.FloatField(default=0.0)
    price = models.FloatField(default=0.0)
    opening_mv = models.FloatField(default=0.0)
    closing_mv = models.FloatField(default=0.0)
    weight = models.FloatField(default=0.0)

