from django.db import models
from datetime import datetime
from instrument.models import Instruments, Tickers
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

class Portfolio(models.Model):
    portfolio_name = models.CharField(max_length=30, default="")
    portfolio_code = models.CharField(max_length=30, null=True, blank=True)
    portfolio_type = models.CharField(max_length=30, default="")
    status = models.CharField(max_length=30, default="Not Funded")
    currency = models.CharField(max_length=30, default="")
    creation_date = models.DateField(default=datetime.now, blank=True)
    inception_date = models.DateField(null=True)
    perf_start_date = models.DateField(null=True)
    termination_date = models.DateField(null=True)
    is_terminated = models.CharField(max_length=30, default=False)
    owner = models.CharField(max_length=30, default="")
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column="user", default=1)
    manager = models.CharField(max_length=30, default="")
    public = models.BooleanField(default=False)
    trading_allowed = models.BooleanField(default=False)
    multicurrency_allowed = models.BooleanField(default=False)
    weekend_valuation = models.BooleanField(default=False)
    valuation_frequency = models.CharField(max_length=30, default="Daily")
    calc_holding = models.BooleanField(default=False)
    description = models.CharField(max_length=2000, default="")
    pricing_tolerance = models.IntegerField(default=30)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
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
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, null=True, blank=True, default=None)
    pos_val = models.FloatField(default=0.0)
    cash_val = models.FloatField(default=0.0)
    margin = models.FloatField(default=0.0)
    accured_income = models.FloatField(default=0.0)
    short_liab = models.FloatField(default=0.0)
    long_liab = models.FloatField(default=0.0)
    accured_expenses = models.FloatField(default=0.0)
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

    # Must to have fields
    portfolio_code = models.CharField(max_length=30, default="")
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, null=True, blank=True, default=None)
    security = models.ForeignKey(Instruments, on_delete=models.CASCADE)
    quantity = models.FloatField(default=0.0)
    trade_date = models.DateField(null=True)
    transaction_type = models.CharField(max_length=30, default="")

    # Optional fields
    price = models.FloatField(default=0.0)  # Needed -> Inst Tran
    fx_rate = models.FloatField(default=1.0) # Needed -> Inst Tran
    open_status = models.CharField(max_length=50, default="Open")  # Needed -> Inst Tran -> Parent
    transaction_link_code = models.IntegerField(default=0) # Needed -> Inst Tran -> Child
    margin_rate = models.FloatField(default=0.0) # Ez csak derivativáknál kell


    trading_cost = models.FloatField(default=0.0)
    financing_cost = models.FloatField(default=0.0)
    account_id = models.IntegerField(null=True)
    broker_id = models.IntegerField(null=True)
    broker = models.CharField(max_length=30, default="")
    settlement_date = models.DateField(null=True)
    is_active = models.BooleanField(default=True)
    currency = models.CharField(max_length=30, default="") # Ez az instrumentum Currencyje lesz, nem kell küldeni front endről

    # Calculated fields
    created_on = models.DateTimeField(auto_now_add=True)
    mv = models.FloatField(default=0.0)
    local_mv = models.FloatField(default=0.0)
    bv = models.FloatField(default=0.0)
    local_bv = models.FloatField(default=0.0)
    net_cashflow = models.FloatField(default=0.0)
    local_cashflow = models.FloatField(default=0.0)
    margin_balance = models.FloatField(default=0.0)

    def new_cash_transaction(self, *args, **kwargs):
        try:
            instrument = Instruments.objects.get(id=self.security_id)
            if instrument.group != 'Cash' and instrument.type != 'Cash':
                return "Instrument is not a Cash/Cash security"

        except ObjectDoesNotExist:
            return  "Instrument ID does not exist (" + str(self.security_id) + ")"

        try:
            portfolio = Portfolio.objects.get(id=self.portfolio_id)
            if instrument.currency != portfolio.currency and portfolio.multicurrency_allowed is False:
                return f"Multicurrency is not allowed for portfolio. Port ccy ({portfolio.currency}) Inst ccy ({instrument.currency})"
        except ObjectDoesNotExist:
            return "Portfolio ID does not exist (" + str(self.portfolio_id) + ")"

        if self.transaction_link_code == 0:
            super().save(*args, **kwargs)  # Save once to generate ID
            self.transaction_link_code = self.id  # Now the ID exists

        multiplier = -1 if self.transaction_type in ['Redemption', 'Interest Paid', 'Commission', 'Financing'] else 1

        # Ensure quantity is not None (avoid TypeError)
        if self.quantity is not None:
            self.quantity *= multiplier

        self.currency = instrument.currency
        self.price = 1
        self.mv = self.local_mv = self.bv = self.local_bv = self.quantity
        self.net_cashflow = self.local_cashflow = self.quantity
        self.open_status = 'Close'
        self.is_active = False

        super().save(*args, **kwargs)

        Cash(
            date=self.trade_date,
            portfolio_code=self.portfolio_code,
            base_mv=self.net_cashflow,
            local_mv=self.local_cashflow,
            type=self.transaction_type,
            transaction_id=self.id
        ).save()
        return "New capital transaction is created"

    def new_parent_transaction(self, *args, **kwargs):
        try:
            instrument = Instruments.objects.get(id=self.security_id)
            if instrument.group == 'Cash':
                return "Instrument is a Cash security"
        except ObjectDoesNotExist:
            return  "Instrument ID does not exist (" + str(self.security_id) + ")"

        if self.transaction_link_code == 0:
            super().save(*args, **kwargs)  # Save once to generate ID
            self.transaction_link_code = self.id  # Now the ID exists

        # Here decides on a particular asset class how to calculate mv and bv and cash flows
        if instrument.group == "CFD":
            self.derivatives_transaction()

        return "Parent Instrument Transaction is created"

    def new_child_transaction(self, parent_id):
        try:
            instrument = Instruments.objects.get(id=self.security_id)
            if instrument.group == 'Cash':
                return "Instrument is a Cash security"
        except ObjectDoesNotExist:
            return  "Instrument ID does not exist (" + str(self.security_id) + ")"

        # Checking if it is an existing parent transaction
        try:
            self.parent_transaction = Transaction.objects.get(id=parent_id)
        except ObjectDoesNotExist:
            return  "Parent ID does not exist (" + str(parent_id) + ")"

        self.is_active = False
        self.open_status = 'Close'

        if self.parent_transaction.transaction_type == 'Purchase':
            self.transaction_type = 'Sale'
        if self.parent_transaction.transaction_type == 'Sale':
            self.transaction_type = 'Purchase'

        return "Child Instrument Transaction"

    def save(self, *args, **kwargs):

        # Amikor elmentek egy uj recordot akkor minden egyes esetbe a megadott instrumentum ID alapjan az adatbázisbol
        # kinyeri az isntrumentum adatait

        instrument = Instruments.objects.get(id=self.security_id)

        if self.transaction_link_code == 0:

            # Ez mondja meg hogy egy parent tranzakció

            super().save(*args, **kwargs)
            self.transaction_link_code = self.id
        else:
            # Children tranzakció
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

        # This tells how capital cash transactions are calulcated and saved

        multiplier = -1 if self.transaction_type in ['Redemption', 'Interest Paid', 'Commission', 'Financing'] else 1
        self.quantity *= multiplier
        self.price = 1
        self.mv = self.local_mv = self.bv = self.local_bv = self.quantity
        self.net_cashflow = self.local_cashflow = self.quantity
        self.open_status = 'Close'
        self.is_active = False
        super().save(*args, **kwargs)

    def derivatives_transaction(self, *args, **kwargs):

        # This tells the logic how derivative security transactions are calculated

        ticker = Tickers.objects.get(inst_code=self.security_id, source=self.broker)
        self.margin_rate = ticker.margin
        cf_multiplier = -1 if self.open_status in ['Open'] else 1
        self.quantity *= -1 if self.transaction_type in ['Sale'] else 1


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

    def save_cashflow(self):
        # this saves the transaction related cashflow to portfolios cash table where cash movements are tracked
        Cash(
            date=self.trade_date,
            portfolio_code=self.portfolio_code,
            base_mv=self.net_cashflow,
            local_mv=self.local_cashflow,
            type=self.transaction_type,
            transaction_id=self.id
        ).save()

class TransactionPnl(models.Model):
    transaction_id = models.IntegerField(default=0)
    portfolio_code = models.CharField(max_length=30, default="")
    security = models.IntegerField(default=0)
    pnl = models.FloatField(default=0.0)
    date = models.DateField(null=True)


class Cash(models.Model):
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
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, null=True, blank=True, default=None)
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
    pos_lev = models.FloatField(default=0.0)
    ugl = models.FloatField(default=0.0)
    rgl = models.FloatField(default=0.0)
    margin_rate = models.FloatField(default=0.0)

class TotalReturn(models.Model):
    portfolio_code = models.CharField(max_length=30, default="")
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, null=True, blank=True, default=None)
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
