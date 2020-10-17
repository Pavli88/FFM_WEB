from django.db import models


class Instruments(models.Model):
    instrument_name = models.CharField(max_length=30, default="")
    instrument_type = models.CharField(max_length=30, default="")
    source = models.CharField(max_length=30, default="")
