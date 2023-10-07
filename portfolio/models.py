from django.db import models
from datetime import datetime
import pandas as pd
from django.db.models import Sum
from datetime import timedelta
from datetime import date
from django.db import connection
from instrument.models import Instruments


class Portfolio(models.Model):
    portfolio_name = models.CharField(max_length=30, default="")
    portfolio_code = models.CharField(max_length=30, unique=True)
    portfolio_type = models.CharField(max_length=30, default="")
    status = models.CharField(max_length=30, default="Not Funded")
    currency = models.CharField(max_length=30, default="")
    creation_date = models.DateField(default=datetime.now, blank=True)
    inception_date = models.DateField(null=True)
    perf_start_date = models.DateField(null=True)
    termination_date = models.DateField(null=True)
    is_terminated = models.CharField(max_length=30, default=False)
    owner = models.CharField(max_length=30, default="")
    manager = models.CharField(max_length=30, default="")
    public = models.BooleanField(default=False)
    is_automated = models.BooleanField(default=False)
    weekend_valuation = models.BooleanField(default=False)
    valuation_frequency = models.CharField(max_length=30, default="Daily")
    calc_holding = models.BooleanField(default=False)
    description = models.CharField(max_length=2000, default="")


class Robots(models.Model):
    portfolio_code = models.CharField(max_length=30, default="")
    inst_id = models.IntegerField()
    ticker_id = models.IntegerField()
    broker_account_id = models.IntegerField()


class Performance(models.Model):
    portfolio_code = models.CharField(max_length=30, default="")
    one_month = models.FloatField(default=0.0)
    date = models.DateField(auto_now=True)


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
    period_return = models.FloatField(default=0.0)
    pnl = models.FloatField(default=0.0)
    date = models.DateField()
    holding_nav = models.FloatField(default=0.0)


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
    security = models.IntegerField(default=0)
    sec_group = models.CharField(max_length=30, default="")
    option = models.CharField(max_length=30, default="")
    quantity = models.FloatField(default=0.0)
    price = models.FloatField(default=0.0)
    mv = models.FloatField(default=0.0)
    local_mv = models.FloatField(default=0.0)
    trade_date = models.DateField(null=True)
    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    currency = models.CharField(max_length=30, default="")
    trading_cost = models.FloatField(default=0.0)
    financing_cost = models.FloatField(default=0.0)
    transaction_type = models.CharField(max_length=30, default="")
    transaction_link_code = models.IntegerField(default=0)
    open_status = models.CharField(max_length=50, default="")
    account_id = models.IntegerField(null=True)
    broker_id = models.IntegerField(null=True)
    net_cashflow = models.FloatField(default=0.0)
    local_cashflow = models.FloatField(default=0.0)
    margin_balance = models.FloatField(default=0.0)
    realized_pnl = models.FloatField(default=0.0)
    local_pnl = models.FloatField(default=0.0)
    margin = models.FloatField(default=0.0)
    fx_rate = models.FloatField(default=1.0)
    fx_pnl = models.FloatField(default=0.0)

    def save_cashflow(self, *args, **kwargs):
        multiplier = 1.0
        if self.transaction_type == 'Redemption' or self.transaction_type == 'Interest Paid' or self.transaction_type == 'Commission':
            multiplier = -1.0
        self.price = 1
        self.mv = self.quantity
        self.local_mv = self.quantity
        self.net_cashflow = self.quantity * multiplier
        self.local_cashflow = self.quantity * multiplier
        self.open_status = 'Closed'
        self.sec_group = 'Cash'
        self.is_active = False
        super().save(*args, **kwargs)

    def save_new_transaction(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def save_linked_transaction(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def save(self, *args, **kwargs):
        # if self.sec_group == 'Cash':
        #     if self.transaction_type == 'Redemption' or self.transaction_type == 'Interest Paid' or self.transaction_type == 'Commission':
        #         self.quantity = float(self.quantity) * -1
        # elif self.sec_group == 'CFD':
        #     if self.transaction_link_code != 0:
        #         self.quantity = float(self.quantity) * -1
        # else:
        #     self.quantity = abs(float(self.quantity))

        # self.mv = float(self.quantity) * float(self.price)

        multiplier = 1
        if self.transaction_type == 'Redemption' or self.transaction_type == 'Interest Paid' or self.transaction_type == 'Commission':
            multiplier = -1

        if self.sec_group == 'Cash':
            self.price = 1
            self.mv = self.quantity * multiplier
            self.net_cashflow = self.quantity * multiplier
            self.local_cashflow = self.quantity * multiplier
            self.local_mv = self.quantity * multiplier
            self.open_status = 'Closed'
        super().save(*args, **kwargs)


class TransactionPnl(models.Model):
    transaction_id = models.IntegerField(default=0)
    portfolio_code = models.CharField(max_length=30, default="")
    security = models.IntegerField(default=0)
    pnl = models.FloatField(default=0.0)
    closing_date = models.DateTimeField(auto_now_add=True)


class Positions(models.Model):
    portfolio_name = models.CharField(max_length=30, default="")
    security = models.IntegerField(default=0)
    quantity = models.FloatField(default=0.0)
    date = models.DateTimeField(auto_now_add=True)


class PortGroup(models.Model):
    parent_id = models.IntegerField()
    children_id = models.IntegerField()
    connection_id = models.CharField(max_length=30, default="", unique=True)
    type = models.CharField(max_length=30, default="")


class Holding(models.Model):
    date = models.DateField()
    portfolio_code = models.CharField(max_length=30)
    data = models.JSONField(null=True)


class TotalReturn(models.Model):
    portfolio_code = models.CharField(max_length=30, default="")
    total_return = models.FloatField(default=0.0)
    end_date = models.DateField(null=True)
    period = models.CharField(max_length=30, default="")

# models.signals.post_save.connect(create_transaction_related_cashflow, sender=Transaction)
# models.signals.post_delete.connect(calculate_cash_holding_after_delete, sender=Transaction)