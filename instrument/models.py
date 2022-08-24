from django.db import models


class Instruments(models.Model):
    instrument_name = models.CharField(max_length=30, default="")
    inst_code = models.CharField(max_length=30, unique=True)
    instrument_type = models.CharField(max_length=30, default="")
    source = models.CharField(max_length=30, default="")
    currency = models.CharField(max_length=30, default="")
    source_code = models.CharField(max_length=30, default="")
    instrument_sub_type = models.CharField(max_length=30, default="")


class Prices(models.Model):
    inst_code = models.CharField(max_length=30, default="")
    price = models.FloatField(default=0.0)
    source = models.CharField(max_length=30, default="")
    date = models.DateField()


class Tickers(models.Model):
    inst_code = models.CharField(max_length=30, default="")
    internal_ticker = models.CharField(max_length=30, default="", unique=True)
    source_ticker = models.CharField(max_length=30, default="")
    source = models.CharField(max_length=30, default="")