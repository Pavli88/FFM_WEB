# Generated by Django 3.0.5 on 2020-04-28 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mysite', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='brokeraccounts',
            name='env',
            field=models.CharField(default='', max_length=100),
        ),
    ]
