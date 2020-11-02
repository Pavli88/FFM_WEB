# Generated by Django 3.0.5 on 2020-10-25 17:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('robots', '0011_auto_20201015_1906'),
    ]

    operations = [
        migrations.RenameField(
            model_name='balance',
            old_name='balance',
            new_name='cash_flow',
        ),
        migrations.RenameField(
            model_name='balance',
            old_name='daily_cash_flow',
            new_name='close_balance',
        ),
        migrations.RenameField(
            model_name='balance',
            old_name='daily_pnl',
            new_name='opening_balance',
        ),
        migrations.AddField(
            model_name='balance',
            name='realized_pnl',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='balance',
            name='ret',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='balance',
            name='unrealized_pnl',
            field=models.FloatField(default=0.0),
        ),
    ]