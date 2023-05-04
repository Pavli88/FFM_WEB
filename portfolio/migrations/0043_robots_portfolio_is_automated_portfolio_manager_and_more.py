# Generated by Django 4.1.5 on 2023-03-16 00:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0042_portgroup_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='Robots',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('portfolio_code', models.CharField(default='', max_length=30)),
                ('inst_id', models.IntegerField()),
                ('ticker_id', models.IntegerField()),
                ('broker_account_id', models.IntegerField()),
            ],
        ),
        migrations.AddField(
            model_name='portfolio',
            name='is_automated',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='portfolio',
            name='manager',
            field=models.CharField(default='', max_length=30),
        ),
        migrations.AddField(
            model_name='portfolio',
            name='owner',
            field=models.CharField(default='', max_length=30),
        ),
        migrations.AddField(
            model_name='portfolio',
            name='public',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='portfolio',
            name='status',
            field=models.CharField(default='active', max_length=30),
        ),
    ]