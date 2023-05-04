# Generated by Django 4.2 on 2023-04-27 09:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_alter_brokeraccounts_account_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='brokeraccounts',
            name='margin_account',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='brokeraccounts',
            name='margin_percentage',
            field=models.FloatField(default=0.0),
        ),
    ]