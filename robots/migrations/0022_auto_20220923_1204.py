# Generated by Django 3.2.15 on 2022-09-23 10:04

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('robots', '0021_alter_robots_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='balance',
            name='robot_name',
        ),
        migrations.AddField(
            model_name='balance',
            name='robot_id',
            field=models.IntegerField(default=0),
        ),
    ]
