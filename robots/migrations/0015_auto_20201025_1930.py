# Generated by Django 3.0.5 on 2020-10-25 18:30

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('robots', '0014_auto_20201025_1917'),
    ]

    operations = [
        migrations.AlterField(
            model_name='robotcashflow',
            name='date',
            field=models.DateField(default=datetime.date.today),
        ),
    ]
