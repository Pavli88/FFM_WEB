# Generated by Django 3.2.7 on 2022-08-24 08:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_accountcashflow_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='Brokers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('broker', models.CharField(default='', max_length=50)),
                ('broker_code', models.CharField(default='', max_length=50, unique=True)),
            ],
        ),
    ]
