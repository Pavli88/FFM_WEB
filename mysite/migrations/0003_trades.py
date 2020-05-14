# Generated by Django 3.0.5 on 2020-05-03 18:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mysite', '0002_brokeraccounts_env'),
    ]

    operations = [
        migrations.CreateModel(
            name='Trades',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('security', models.CharField(default='', max_length=30)),
                ('robot', models.CharField(default='', max_length=30)),
                ('quantity', models.FloatField(default=0.0)),
                ('strategy', models.CharField(default='', max_length=30)),
                ('status', models.CharField(default='', max_length=30)),
                ('pnl', models.FloatField(default=0.0)),
                ('open_price', models.FloatField(default=0.0)),
                ('close_price', models.FloatField(default=0.0)),
                ('open_time', models.DateTimeField(auto_now=True)),
                ('close_time', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]