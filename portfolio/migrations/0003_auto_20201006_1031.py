# Generated by Django 3.0.5 on 2020-10-06 08:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0002_auto_20201006_0959'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cashflow',
            old_name='port_id',
            new_name='portfolio_name',
        ),
    ]
