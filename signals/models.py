from django.db import models

# Create your models here.


class Strategies(models.Model):
    name = models.CharField(max_length=300, unique=True)
    location = models.CharField(max_length=300, unique=True)
    description = models.TextField()
    args = models.TextField()