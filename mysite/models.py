from django.db import models

"Restarting migration"
"python manage.py migrate --fake robots zero"


class BrokerAccounts(models.Model):
    broker_name = models.CharField(max_length=30, default="")
    account_number = models.CharField(max_length=50, default="")
    access_token = models.CharField(max_length=100, default="")
    env = models.CharField(max_length=100, default="")
