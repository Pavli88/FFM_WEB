# Generated by Django 3.0.5 on 2020-10-13 21:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('robots', '0008_balance_cashflow'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='CashFlow',
            new_name='RobotCashFlow',
        ),
    ]