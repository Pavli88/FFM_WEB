# Generated by Django 5.1.2 on 2025-03-26 08:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0012_holding_beg_market_price_holding_beg_quantity'),
    ]

    operations = [
        migrations.AddField(
            model_name='holding',
            name='beg_bv',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='holding',
            name='beg_mv',
            field=models.FloatField(default=0.0),
        ),
    ]
