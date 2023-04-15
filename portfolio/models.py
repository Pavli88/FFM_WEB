from django.db import models
from datetime import datetime


class Portfolio(models.Model):
    portfolio_name = models.CharField(max_length=30, default="")
    portfolio_code = models.CharField(max_length=30, unique=True)
    portfolio_type = models.CharField(max_length=30, default="")
    status = models.CharField(max_length=30, default="active")
    currency = models.CharField(max_length=30, default="")
    creation_date = models.DateField(default=datetime.now, blank=True)
    inception_date = models.DateField(null=True)
    termination_date = models.DateField(null=True)
    is_terminated = models.CharField(max_length=30, default=False)
    owner = models.CharField(max_length=30, default="")
    manager = models.CharField(max_length=30, default="")
    public = models.BooleanField(default=False)
    is_automated = models.BooleanField(default=False)


class Robots(models.Model):
    portfolio_code = models.CharField(max_length=30, default="")
    inst_id = models.IntegerField()
    ticker_id = models.IntegerField()
    broker_account_id = models.IntegerField()


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
    date = models.DateField()


class Trade(models.Model):
    portfolio_code = models.CharField(max_length=30, default="")
    security = models.IntegerField(default=0)
    quantity = models.FloatField(default=0.0)
    price = models.FloatField(default=0.0)
    mv = models.FloatField(default=0.0)
    date = models.DateField()
    trading_cost = models.FloatField(default=0.0)
    transaction_type = models.CharField(max_length=30, default="")
    transaction_link_code = models.CharField(max_length=50, default="")


class Transaction(models.Model):
    portfolio_code = models.CharField(max_length=30, default="")
    security = models.CharField(max_length=30, default="")
    quantity = models.FloatField(default=0.0)
    price = models.FloatField(default=0.0)
    mv = models.FloatField(default=0.0)
    trade_date = models.DateTimeField(null=True)
    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    currency = models.CharField(max_length=30, default="")
    trading_cost = models.FloatField(default=0.0)
    transaction_type = models.CharField(max_length=30, default="")
    transaction_link_code = models.CharField(max_length=50, default="")

    def save(self, *args, **kwargs):
        multiplier = 1
        if self.transaction_type == 'Dividend':
            self.price = 1
        if self.transaction_type == 'Sale' or self.transaction_type == 'Redemption':
            self.quantity = self.quantity * -1

        self.mv = self.quantity * self.price
        super().save(*args, **kwargs)


def create_transaction_related_cashflow(instance, **kwargs):
    print("TRANSACTION RELATED")
    print(instance)
    print(instance.transaction_type)
    if instance.transaction_type == 'Purchase' or instance.transaction_type == 'Sale':
        Transaction(portfolio_code=instance.portfolio_code,
                    security='CASH',
                    quantity=instance.mv * -1,
                    price=1,
                    currency=instance.currency,
                    transaction_type=instance.transaction_type + ' Settlement',
                    transaction_link_code=instance.id).save()


models.signals.post_save.connect(create_transaction_related_cashflow, sender=Transaction)


class Positions(models.Model):
    portfolio_name = models.CharField(max_length=30, default="")
    security = models.IntegerField(default=0)
    quantity = models.FloatField(default=0.0)
    date = models.DateField()


class PortGroup(models.Model):
    parent_id = models.IntegerField()
    children_id = models.IntegerField()
    connection_id = models.CharField(max_length=30, default="", unique=True)
    type = models.CharField(max_length=30, default="")


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
