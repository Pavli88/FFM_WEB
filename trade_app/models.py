from django.db import models
from portfolio.models import Portfolio
from accounts.models import Brokers, BrokerAccounts

class Notifications(models.Model):
    portfolio_code = models.CharField(max_length=50, default="")
    message = models.CharField(max_length=500, default="")
    sub_message = models.CharField(max_length=50, default="")
    security = models.CharField(max_length=50, default="")
    broker_name = models.CharField(max_length=50, default="")
    date = models.DateField(auto_now=True)
    time = models.DateTimeField(auto_now=True)

class Signal(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('EXECUTED', 'Executed'),
        ('FAILED', 'Failed'),
    ]

    SOURCE_CHOICES = [
        ('INTERNAL', 'Internal'),
        ('EXTERNAL', 'External'),
    ]

    TYPE_CHOICES = [
        ('OPEN', 'Open'),
        ('CLOSE', 'Close'),
    ]

    portfolio = models.ForeignKey(
        Portfolio,
        on_delete=models.CASCADE,
        related_name='signals',
        null=True, blank=True, default=None
    )
    type = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    source = models.CharField(max_length=10, choices=SOURCE_CHOICES, default='INTERNAL')
    raw_data = models.JSONField()
    error_message = models.TextField(blank=True, null=True)
    executed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Signal #{self.id} – {self.portfolio.portfolio_code if self.portfolio else 'No Portfolio'}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('EXECUTED', 'Executed'),
        ('REJECTED', 'Rejected'),
        ('FAILED', 'Failed'),
        ('PARTIAL', 'Partial'),
    ]

    signal = models.ForeignKey(Signal, on_delete=models.SET_NULL, null=True, related_name='orders')

    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    broker_account = models.ForeignKey(BrokerAccounts, on_delete=models.SET_NULL, null=True, related_name='orders')

    security_id = models.IntegerField()
    symbol = models.CharField(max_length=50)
    side = models.CharField(max_length=4, choices=[('BUY', 'Buy'), ('SELL', 'Sell')])

    quantity = models.DecimalField(max_digits=20, decimal_places=4)
    executed_price = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)
    fx_rate = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)

    broker_order_id = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    error_message = models.TextField(null=True, blank=True)
    executed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} – {self.symbol} – {self.status}"