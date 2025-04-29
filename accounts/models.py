from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class BrokerAccounts(models.Model):
    broker_name = models.CharField(max_length=30, default="")
    account_name = models.CharField(max_length=30, default="")
    account_number = models.CharField(max_length=50, default="")
    access_token = models.CharField(max_length=100, default="")
    account_type = models.CharField(max_length=100, default="")
    env = models.CharField(max_length=100, default="")
    currency = models.CharField(max_length=100, default="")
    owner = models.CharField(max_length=30, default="")
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column="user", null=True, blank=True, default=None)
    margin_account = models.BooleanField(default=False)
    margin_percentage = models.FloatField(default=0.0)

class Brokers(models.Model):
    broker = models.CharField(max_length=100, default="")
    broker_code = models.CharField(max_length=50, default="")
    type = models.CharField(max_length=100, default="")
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column="user", null=True, blank=True, default=None)
    api_support = models.BooleanField(default=False)

    def clean(self):
        """Enforce that if a broker_code exists with api_support=True, no other record can use it."""
        if Brokers.objects.filter(broker_code=self.broker_code, api_support=True).exclude(id=self.id).exists():
            raise ValidationError({"broker_code": "This broker_code is already used in a record with API support."})

    def save(self, *args, **kwargs):
        """Run clean before saving to enforce validation."""
        self.clean()
        super().save(*args, **kwargs)

class BrokerCredentials(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column="user", null=True, blank=True, default=None)
    broker = models.ForeignKey(Brokers, on_delete=models.CASCADE, db_column="broker", null=True, blank=True, default=None)
    api_token = models.CharField(max_length=100, default="")
    environment = models.CharField(max_length=100, default="")
    email = models.EmailField(max_length=254, null=True, blank=True)
    password = models.CharField(max_length=128, null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)