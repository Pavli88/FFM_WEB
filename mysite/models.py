from django.db import models
import datetime
from django.contrib.auth.models import AbstractUser, Group, Permission
import uuid
from django.contrib.auth.models import User


class Trades(models.Model):
    security = models.CharField(max_length=30, default="")
    robot = models.CharField(max_length=30, default="")
    quantity = models.FloatField(default=0.0)
    strategy = models.CharField(max_length=30, default="")
    status = models.CharField(max_length=30, default="")
    pnl = models.FloatField(default=0.0)
    open_price = models.FloatField(default=0.0)
    close_price = models.FloatField(default=0.0)
    open_time = models.DateTimeField(auto_now_add=True)
    close_time = models.DateTimeField(auto_now=True)
    time_frame = models.CharField(max_length=30, default="")
    side = models.CharField(max_length=30, default="")
    broker_id = models.IntegerField(default=0)
    broker = models.CharField(max_length=30, default="")
    sl = models.FloatField(default=0.0)


class HomePageDefault(models.Model):
    account_number = models.CharField(max_length=30, default="")


class Settings(models.Model):
    ov_status = models.BooleanField()
    ov_st_time = models.TimeField()
    ov_en_time = models.TimeField()


class SystemMessages(models.Model):
    msg_type = models.CharField(max_length=100, default="")
    msg_sub_type = models.CharField(max_length=100, default="")
    msg = models.CharField(max_length=200, default="")
    date = models.DateField(auto_now=True)
    verified = models.BooleanField(default=False)


class ProcessInfo(models.Model):
    name = models.CharField(max_length=100, default="")
    broker_id = models.CharField(max_length=100, default="")
    type = models.CharField(max_length=100, default="")
    is_done = models.BooleanField(blank=False, default=False )
    run_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(auto_now=True)
    msg = models.CharField(max_length=100, default="")


class Exceptions(models.Model):
    exception_level = models.CharField(max_length=100, default="")
    entity_code = models.CharField(max_length=100, default="")
    exception_type = models.CharField(max_length=100, default="")
    process = models.CharField(max_length=100, default="")
    status = models.CharField(max_length=100, default="")
    calculation_date = models.DateField(default=datetime.date.today)
    creation_date = models.DateTimeField()
    security_id = models.CharField(max_length=100, default="")

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    reset_token = models.CharField(max_length=255, blank=True, null=True)  # Token field
    token_created_at = models.DateTimeField(blank=True, null=True)  # Token creation timestamp

