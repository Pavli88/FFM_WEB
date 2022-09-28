# Generated by Django 3.2.15 on 2022-09-20 16:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('robots', '0018_robots_strategy_params'),
    ]

    operations = [
        migrations.AddField(
            model_name='robots',
            name='robot_code',
            field=models.CharField(default='', max_length=20),
        ),
        migrations.AlterField(
            model_name='robots',
            name='name',
            field=models.CharField(default='', max_length=30),
        ),
    ]