# Generated by Django 3.2.7 on 2022-08-24 14:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('instrument', '0006_auto_20220817_2145'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tickers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inst_code', models.CharField(default='', max_length=30)),
                ('internal_ticker', models.CharField(default='', max_length=30, unique=True)),
                ('source_ticker', models.CharField(default='', max_length=30)),
                ('source', models.CharField(default='', max_length=30)),
            ],
        ),
    ]
