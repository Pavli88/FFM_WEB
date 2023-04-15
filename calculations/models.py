from django.db import models
import datetime


class PortfolioProcessStatus(models.Model):
    date = models.DateField()
    portfolio_code = models.CharField(max_length=30, default="")
    cash_holding = models.CharField(max_length=30, default="")
    position = models.CharField(max_length=30, default="")
    portfolio_holding = models.CharField(max_length=30, default="")
