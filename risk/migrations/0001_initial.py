# Generated by Django 3.0.5 on 2020-05-21 13:43

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AccountRisk',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account', models.CharField(default='', max_length=50)),
                ('daily_risk_limit', models.FloatField(default=0.0)),
            ],
        ),
    ]
