from django.db import models
from datetime import datetime
import pandas as pd
from django.db.models import Sum
from datetime import timedelta
from datetime import date
from django.db import connection
from instrument.models import Instruments, Tickers


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
    pricing_tolerance = models.IntegerField(default=30)


class TradeRoutes(models.Model):
    portfolio_code = models.CharField(max_length=30, default="")
    inst_id = models.IntegerField()
    ticker_id = models.IntegerField()
    broker_account_id = models.IntegerField()
    is_active = models.BooleanField(default=False)
    quantity = models.IntegerField(default=1)


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
    unrealized_pnl = models.FloatField(default=0.0)
    date = models.DateField()
    holding_nav = models.FloatField(default=0.0)


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

    def save_transaction(self, **kwargs):
        if kwargs['transaction'] == 'new' or kwargs['transaction'] == 'update':
            multiplier = 1
            if self.transaction_type == 'Purchase' or self.sec_group == 'CFD':
                multiplier = -1
            if self.sec_group == 'CFD':
                ticker = Tickers.objects.get(inst_code=self.security, source=kwargs['broker_name'])
                self.margin = ticker.margin
                self.net_cashflow = round(float(self.quantity) * float(self.price) * ticker.margin * float(self.fx_rate), 5) * multiplier
                self.local_cashflow = round(float(self.quantity) * float(self.price) * ticker.margin, 5) * multiplier
                self.margin_balance = round(float(self.quantity) * float(self.price) * (1 - ticker.margin), 5)
            else:
                self.net_cashflow = round(float(self.quantity) * float(self.price) * float(self.fx_rate), 5) * multiplier
                self.local_cashflow = round(float(self.quantity) * float(self.price), 5) * multiplier
            self.mv = round(float(self.quantity) * float(self.price) * float(self.fx_rate), 5)
            self.local_mv = round(float(self.quantity) * float(self.price), 5)

            # Updating Main Transaction
            if 'id' in kwargs:
                self.id = kwargs['id']
                self.created_on = datetime.now()

        if kwargs['transaction'] == 'linked':
            main_transaction = Transaction.objects.get(id=self.transaction_link_code)
            transaction_weight = abs(float(self.quantity) / float(main_transaction.quantity))

            if main_transaction.transaction_type == 'Purchase' or main_transaction.sec_group == 'CFD':
                if main_transaction.transaction_type == 'Purchase':
                    pnl = round(float(self.quantity) * (float(self.price) - float(main_transaction.price)), 5)
                else:
                    pnl = round(float(self.quantity) * (float(main_transaction.price) - float(self.price)), 5)
                net_cf = round((transaction_weight * main_transaction.net_cashflow * -1) + pnl, 5)
                margin_balance = round(transaction_weight * main_transaction.margin_balance * -1, 5)
            else:
                pnl = round(float(self.quantity) * (float(main_transaction.price) - float(self.price)), 5)
                net_cf = round((transaction_weight * main_transaction.net_cashflow * -1) + pnl, 5)
                margin_balance = round(transaction_weight * main_transaction.margin_balance, 5)

            self.realized_pnl = round(pnl * float(self.fx_rate), 5)
            self.local_pnl = round(pnl, 5)
            self.net_cashflow = round(net_cf * float(self.fx_rate), 5)
            self.local_cashflow = round(net_cf, 5)
            self.margin_balance = round(margin_balance, 5)
            self.mv = round(float(self.quantity) * float(self.price) * float(self.fx_rate), 5)
            self.local_mv = round(float(self.quantity) * float(self.price), 5)
            self.fx_pnl = round((float(self.fx_rate) - main_transaction.fx_rate) * main_transaction.quantity, 5)
        super().save()


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