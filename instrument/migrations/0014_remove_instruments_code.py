# Generated by Django 4.2 on 2023-05-13 15:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('instrument', '0013_tickers_margin'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='instruments',
            name='code',
        ),
    ]
