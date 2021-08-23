from django.db import models


class Instruments(models.Model):
    instrument_name = models.CharField(max_length=30, default="")
    inst_code = models.CharField(max_length=30, default="")
    instrument_type = models.CharField(max_length=30, default="")
    source = models.CharField(max_length=30, default="")
    currency = models.CharField(max_length=30, default="")


class Prices(models.Model):
    inst_code = models.CharField(max_length=30, default="")
    price = models.FloatField(default=0.0)
    source = models.CharField(max_length=30, default="")
    date = models.DateField(auto_now=True)