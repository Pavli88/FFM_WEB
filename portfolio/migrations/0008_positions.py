# Generated by Django 3.0.5 on 2020-10-14 18:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0007_auto_20201009_2354'),
    ]

    operations = [
        migrations.CreateModel(
            name='Positions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('portfolio_name', models.CharField(default='', max_length=30)),
                ('security', models.CharField(default='', max_length=30)),
                ('sec_type', models.CharField(default='', max_length=30)),
                ('quantity', models.FloatField(default=0.0)),
                ('date', models.DateField(auto_now=True)),
            ],
        ),
    ]
