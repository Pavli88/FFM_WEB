# Generated by Django 3.2.7 on 2022-08-18 12:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0036_remove_trade_currency'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='trade',
            name='sec_type',
        ),
    ]
