from django.db import models

"Restarting migration"
"python manage.py migrate --fake robots zero"


class Robots(models.Model):
    name = models.CharField(max_length=20)
    strategy = models.CharField(max_length=50, default='')
    security = models.CharField(max_length=50, default='')
    broker = models.CharField(max_length=50, default='')
    status = models.CharField(max_length=50, default='')
    pyramiding_level = models.FloatField(default=0.0)
    in_exp = models.FloatField(default=0.0)







