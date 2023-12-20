from django.db import models


class Notifications(models.Model):
    portfolio_code = models.CharField(max_length=50, default="")
    message = models.CharField(max_length=50, default="")
    sub_message = models.CharField(max_length=50, default="")
    security = models.CharField(max_length=50, default="")
    broker_name = models.CharField(max_length=50, default="")
    date = models.DateField(auto_now=True)
    time = models.DateTimeField(auto_now=True)
