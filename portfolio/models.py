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
    portfolio_code = models.CharField(max_length=30, unique=True, null=True)
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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.portfolio_type == 'Business':
            self.portfolio_code = self.portfolio_code + '_BS'
            PortGroup(portfolio_id=self.id).save()
        if self.portfolio_type == 'Portfolio Group':
            self.portfolio_code = self.portfolio_code + '_GROUP'
        super().save(*args, **kwargs)

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
    pnl = models.FloatField(default=0.0)
    unrealized_pnl = models.FloatField(default=0.0)
    ugl_diff = models.FloatField(default=0.0)
    total_pnl = models.FloatField(default=0.0)
    date = models.DateField()
    holding_nav = models.FloatField(default=0.0)
    cost = models.FloatField(default=0.0)
    subscription = models.FloatField(default=0.0)
    redemption = models.FloatField(default=0.0)
    total_cf = models.FloatField(default=0.0)
    trade_return = models.FloatField(default=0.0)
    price_return = models.FloatField(default=0.0)


class Transaction(models.Model):
    portfolio_code = models.CharField(max_length=30, default="")
    security = models.ForeignKey(Instruments, on_delete=models.CASCADE)
    option = models.CharField(max_length=30, default="")
    quantity = models.FloatField(default=0.0)
    price = models.FloatField(default=0.0)
    mv = models.FloatField(default=0.0)
    local_mv = models.FloatField(default=0.0)
    bv = models.FloatField(default=0.0)
    local_bv = models.FloatField(default=0.0)
    trade_date = models.DateField(null=True)
    settlement_date = models.DateField(null=True)
    is_active = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    currency = models.CharField(max_length=30, default="")
    trading_cost = models.FloatField(default=0.0)
    financing_cost = models.FloatField(default=0.0)
    transaction_type = models.CharField(max_length=30, default="")
    transaction_link_code = models.IntegerField(default=0)
    open_status = models.CharField(max_length=50, default="Open")
    account_id = models.IntegerField(null=True)
    broker_id = models.IntegerField(null=True)
    broker = models.CharField(max_length=30, default="")
    net_cashflow = models.FloatField(default=0.0)
    local_cashflow = models.FloatField(default=0.0)
    margin_balance = models.FloatField(default=0.0)
    margin_rate = models.FloatField(default=0.0)
    fx_rate = models.FloatField(default=1.0)

    def save(self, *args, **kwargs):
        if not self.security:
            raise ValidationError("Security must be provided.")

        instrument = Instruments.objects.get(id=self.security_id)

        if self.transaction_link_code == 0:
            super().save(*args, **kwargs)
            self.transaction_link_code = self.id
        else:
            # Linked transaction
            self.parent_transaction = Transaction.objects.get(id=self.transaction_link_code)
            self.is_active = False
            self.open_status = 'Close'
            if self.parent_transaction.transaction_type == 'Purchase':
                self.transaction_type = 'Sale'
            if self.parent_transaction.transaction_type == 'Sale':
                self.transaction_type = 'Purchase'

        self.currency = instrument.currency

        # Adjust values if the security group is "Cash"
        if instrument.group == "Cash":
            self.cash_transaction()
            self.save_cashflow()
        if instrument.group == "CFD":
            self.derivatives_transaction()

    def save_cashflow(self):
        Cash(
            date=self.trade_date,
            portfolio_code=self.portfolio_code,
            base_mv=self.net_cashflow,
            local_mv=self.local_cashflow,
            type=self.transaction_type,
            transaction_id=self.id
        ).save()

    def calculate_pnl(self):

        if self.parent_transaction.transaction_type == 'Purchase':
            pnl = (float(self.price) - float(self.parent_transaction.price)) * (
                abs(float(self.quantity)))

        if self.parent_transaction.transaction_type == 'Sale':
            pnl = (float(self.parent_transaction.price) - float(self.price)) * abs(float(self.quantity))

        Cash(
            date=self.trade_date,
            portfolio_code=self.portfolio_code,
            base_mv=round(pnl * float(self.fx_rate), 2),
            local_mv=round(pnl, 2),
            type='Trade PnL',
            transaction_id=self.id
        ).save()

    def cash_transaction(self, *args, **kwargs):
        multiplier = -1 if self.transaction_type in ['Redemption', 'Interest Paid', 'Commission'] else 1
        self.quantity *= multiplier
        self.price = 1
        self.mv = self.local_mv = self.bv = self.local_bv = self.quantity
        self.net_cashflow = self.local_cashflow = self.quantity
        self.open_status = 'Close'
        self.is_active = False
        super().save(*args, **kwargs)

    def derivatives_transaction(self, *args, **kwargs):
        ticker = Tickers.objects.get(inst_code=self.security_id, source=self.broker)
        cf_multiplier = -1 if self.open_status in ['Open'] else 1
        self.quantity *= -1 if self.transaction_type in ['Sale'] else 1
        self.margin_rate = ticker.margin

        self.net_cashflow = round(abs(float(self.quantity)) * float(self.price) * (ticker.margin), 5) * float(self.fx_rate) * cf_multiplier
        self.local_cashflow = round(abs(float(self.quantity)) * float(self.price) * (ticker.margin), 5) * cf_multiplier

        self.margin_balance = self.net_cashflow * -1
        self.mv = round(float(self.quantity) * float(self.price) * float(self.fx_rate), 5)
        self.local_mv = round(float(self.quantity) * float(self.price), 5)
        self.bv = 0
        self.local_bv = 0
        super().save(*args, **kwargs)

        # If it is a new transaction it will assign the ID to the INV Num as well
        if self.open_status == 'Close':
            self.calculate_pnl()

    def overwrite(self, *args, **kwargs):
        super().save(*args, **kwargs)

class TransactionPnl(models.Model):
    transaction_id = models.IntegerField(default=0)
    portfolio_code = models.CharField(max_length=30, default="")
    security = models.IntegerField(default=0)
    pnl = models.FloatField(default=0.0)
    date = models.DateField(null=True)


class Positions(models.Model):
    portfolio_code = models.CharField(max_length=30, default="")
    security = models.ForeignKey(Instruments, on_delete=models.CASCADE)
    quantity = models.FloatField(default=0.0)
    date = models.DateTimeField(auto_now_add=True)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, null=True)

class Cash(models.Model):
    portfolio_code = models.CharField(max_length=30, default="")
    type = models.CharField(max_length=30, default="")
    base_mv = models.FloatField(default=0.0)
    local_mv = models.FloatField(default=0.0)
    date = models.DateField(null=True)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, null=True)


class Margin(models.Model):
    # types -> Initial Margin, Mark to Mark valuation
    portfolio_code = models.CharField(max_length=30, default="")
    type = models.CharField(max_length=30, default="")
    base_mv = models.FloatField(default=0.0)
    local_mv = models.FloatField(default=0.0)
    date = models.DateField(null=True)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, null=True)

class UGL(models.Model):
    portfolio_code = models.CharField(max_length=30, default="")
    base_mv = models.FloatField(default=0.0)
    local_mv = models.FloatField(default=0.0)
    date = models.DateField(null=True)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, null=True)

class RGL(models.Model):
    portfolio_code = models.CharField(max_length=30, default="")
    base_mv = models.FloatField(default=0.0)
    local_mv = models.FloatField(default=0.0)
    date = models.DateField(null=True)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, null=True)

class PortGroup(models.Model):
    parent_id = models.IntegerField(default=0)
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, null=True)


class Holding(models.Model):
    portfolio_code = models.CharField(max_length=30)
    date = models.DateField(null=True)
    trd = models.ForeignKey(Transaction, on_delete=models.CASCADE, null=True)
    inv_num = models.IntegerField(default=0)
    trade_type = models.CharField(max_length=30, default="")
    trade_date = models.DateField(null=True)
    instrument = models.ForeignKey(Instruments, on_delete=models.CASCADE, null=True)
    quantity = models.FloatField(default=0.0) # -> Needed for valuation
    trade_price = models.FloatField(default=0.0)
    market_price = models.FloatField(default=0.0) # -> Needed for valuation
    fx_rate = models.FloatField(default=0.0) # -> Needed for valuation
    mv = models.FloatField(default=0.0)
    bv = models.FloatField(default=0.0)
    weight = models.FloatField(default=0.0)
    ugl = models.FloatField(default=0.0)
    rgl = models.FloatField(default=0.0)
    margin_rate = models.FloatField(default=0.0)

class TotalReturn(models.Model):
    portfolio_code = models.CharField(max_length=30, default="")
    total_return = models.FloatField(default=0.0)
    end_date = models.DateField(null=True)
    period = models.CharField(max_length=30, default="")


class SecurityReturn(models.Model):
    portfolio_code = models.CharField(max_length=40, default="")
    date = models.DateField()
    security = models.IntegerField(default=0)
    weight = models.FloatField(default=0.0)
    trade_return = models.FloatField(default=0.0)
    price_return = models.FloatField(default=0.0)
    income_return = models.FloatField(default=0.0)
    fx_return = models.FloatField(default=0.0)
    contribution = models.FloatField(default=0.0)


class Process(models.Model):
    portfolio_code = models.CharField(max_length=40, default="")
    date = models.DateTimeField(auto_now_add=True)
    process = models.CharField(max_length=40, default="")

# models.signals.post_save.connect(create_transaction_related_cashflow, sender=Transaction)
# models.signals.post_delete.connect(calculate_cash_holding_after_delete, sender=Transaction)