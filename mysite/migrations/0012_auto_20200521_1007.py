# Generated by Django 3.0.5 on 2020-05-21 08:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mysite', '0011_settings'),
    ]

    operations = [
        migrations.AddField(
            model_name='trades',
            name='broker',
            field=models.CharField(default='', max_length=30),
        ),
        migrations.AddField(
            model_name='trades',
            name='broker_id',
            field=models.IntegerField(default=0),
        ),
    ]