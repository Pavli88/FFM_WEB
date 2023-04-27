from django.db import models
from datetime import datetime
import pandas as pd
from django.db.models import Sum


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


def calculate_cash_holding(instance, **kwargs):
    print('CALCULATING CASH HOLDING')
    if instance.sec_group == 'Cash':
        print(instance.sec_group, instance.portfolio_code, instance.mv)

        try:
            cash_holding = CashHolding.objects.get(portfolio_code=instance.portfolio_code,
                                                   currency=instance.currency)
            cash_holding.amount = cash_holding.amount + instance.mv
            cash_holding.save()
        except CashHolding.DoesNotExist:
            CashHolding(portfolio_code=instance.portfolio_code,
                        amount=instance.mv,
                        date=instance.trade_date,
                        currency=instance.currency).save()


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
    sec_group = models.CharField(max_length=30, default="")
    quantity = models.FloatField(default=0.0)
    price = models.FloatField(default=0.0)
    mv = models.FloatField(default=0.0)
    trade_date = models.DateField(null=True)
    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    currency = models.CharField(max_length=30, default="")
    trading_cost = models.FloatField(default=0.0)
    transaction_type = models.CharField(max_length=30, default="")
    transaction_link_code = models.CharField(max_length=50, default="")
    open_status = models.CharField(max_length=50, default="")
    account_id = models.IntegerField(null=True)
    broker_id = models.IntegerField(null=True)
    margin = models.FloatField(default=0.0)

    def save(self, *args, **kwargs):
        if (self.transaction_type == 'Sale' or self.transaction_type == 'Redemption' \
                or self.transaction_type == 'Interest Paid' \
                or self.transaction_type == 'Commission'\
                or self.transaction_type == 'Asset Out') and self.sec_group != 'Margin':
            self.quantity = float(self.quantity) * -1
        self.mv = float(self.quantity) * float(self.price)
        super().save(*args, **kwargs)


def create_transaction_related_cashflow(instance, **kwargs):
    print("TRANSACTION RELATED")
    print(instance)
    print(instance.transaction_type)
    if (instance.transaction_type == 'Purchase' or instance.transaction_type == 'Sale') and instance.open_status != 'Closed' and instance.sec_group != 'Margin':
        # if instance.margin == 0.0:
        #     quantity = instance.mv * -1
        # else:
        #     quantity = ((instance.mv / instance.margin) - instance.mv) * -1
        Transaction(portfolio_code=instance.portfolio_code,
                    security='Cash',
                    sec_group='Cash',
                    quantity=instance.quantity,
                    price=1,
                    currency=instance.currency,
                    transaction_type=instance.transaction_type + ' Settlement',
                    transaction_link_code=instance.id,
                    trade_date=instance.trade_date).save()

    if (instance.transaction_type == 'Asset In' or instance.transaction_type == 'Asset Out') and instance.open_status != 'Closed':
        if instance.transaction_type == 'Asset In':
            transaction_type = 'Purchase'
        else:
            transaction_type = 'Sale'
        Transaction(portfolio_code=instance.portfolio_code,
                    security='Margin',
                    sec_group='Margin',
                    quantity=float(instance.quantity) * (1 - float(instance.margin)),
                    price=instance.price,
                    currency=instance.currency,
                    transaction_type=transaction_type,
                    transaction_link_code=instance.id,
                    trade_date=instance.trade_date,
                    margin=1-float(instance.margin)).save()

        Transaction(portfolio_code=instance.portfolio_code,
                    security='Cash',
                    sec_group='Cash',
                    quantity=float(instance.quantity) * float(instance.margin),
                    price=instance.price,
                    currency=instance.currency,
                    transaction_type=transaction_type + ' Settlement',
                    transaction_link_code=instance.id,
                    trade_date=instance.trade_date).save()


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


models.signals.post_save.connect(create_transaction_related_cashflow, sender=Transaction)
models.signals.post_save.connect(calculate_cash_holding, sender=Transaction)