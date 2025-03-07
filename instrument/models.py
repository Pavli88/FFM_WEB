from django.db import models
from django.contrib.auth.models import User

class Instruments(models.Model):
    name = models.CharField(max_length=100, default="")
    group = models.CharField(max_length=30, default="")
    type = models.CharField(max_length=30, default="")
    currency = models.CharField(max_length=30, default="")
    country = models.CharField(max_length=30, default="")
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column="user", null=True, blank=True, default=None)

class Prices(models.Model):
    instrument = models.ForeignKey(Instruments, on_delete=models.CASCADE, null=True)
    price = models.FloatField(default=0.0)
    source = models.CharField(max_length=30, default="")
    date = models.DateField()


class Tickers(models.Model):
    inst_code = models.ForeignKey(Instruments, on_delete=models.CASCADE, db_column="inst_code", null=True, blank=True, default=None)
    source_ticker = models.CharField(max_length=30, default="")
    source = models.CharField(max_length=30, default="")
    margin = models.FloatField(default=0.0)