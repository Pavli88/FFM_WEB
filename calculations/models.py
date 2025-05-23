from django.db import models
import datetime
from portfolio.models import Portfolio
from mysite.models import User

class PortfolioProcessStatus(models.Model):
    date = models.DateField()
    portfolio_code = models.CharField(max_length=30, default="")
    cash_holding = models.CharField(max_length=30, default="")
    position = models.CharField(max_length=30, default="")
    portfolio_holding = models.CharField(max_length=30, default="")


class ProcessAudit(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, null=True, blank=True)
    process = models.CharField(max_length=50)
    run_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    run_at = models.DateTimeField(auto_now_add=True)
    valuation_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('Started', 'Started'), ('Completed', 'Completed'), ('Failed', 'Failed')])
    message = models.TextField(blank=True)
    duration_seconds = models.FloatField(null=True, blank=True)
    trigger_type = models.CharField(max_length=30, choices=[('Manual', 'Manual'), ('Scheduled', 'Scheduled'), ('Frontend', 'Frontend')], default='Manual')

class ProcessException(models.Model):
    audit = models.ForeignKey(ProcessAudit, related_name='exceptions', on_delete=models.CASCADE)
    exception_type = models.CharField(max_length=200)  # Pl. 'Missing Price', 'Missing FX Rate'
    message = models.TextField()  # Pl. instrument neve vagy ID, vagy részletes hiba
    severity = models.CharField(max_length=20, choices=[('Error', 'Error'), ('Warning', 'Warning'), ('Completed', 'Completed'), ('Alert', 'Alert')], default='Error')
    process_date = models.DateField(null=True, blank=True)