# Generated by Django 3.0.5 on 2021-08-23 19:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0029_auto_20210709_2007'),
    ]

    operations = [
        migrations.CreateModel(
            name='PortfolioHoldings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('portfolio_code', models.CharField(max_length=30, unique=True)),
                ('portfolio_name', models.CharField(default='', max_length=30)),
                ('date', models.DateField()),
                ('security', models.IntegerField(default=0)),
                ('quantity', models.FloatField(default=0.0)),
                ('price', models.FloatField(default=0.0)),
                ('opening_mv', models.FloatField(default=0.0)),
                ('closing_mv', models.FloatField(default=0.0)),
                ('weight', models.FloatField(default=0.0)),
            ],
        ),
    ]