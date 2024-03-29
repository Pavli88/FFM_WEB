# Generated by Django 3.0.5 on 2020-12-03 19:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0016_auto_20201203_1451'),
    ]

    operations = [
        migrations.RenameField(
            model_name='nav',
            old_name='amount',
            new_name='accured_expenses',
        ),
        migrations.AddField(
            model_name='nav',
            name='accured_income',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='nav',
            name='cash_val',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='nav',
            name='long_liab',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='nav',
            name='nav_per_share',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='nav',
            name='pos_val',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='nav',
            name='short_liab',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='nav',
            name='total',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='nav',
            name='units',
            field=models.FloatField(default=0.0),
        ),
    ]
