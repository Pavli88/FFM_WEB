# Generated by Django 3.0.5 on 2020-10-14 19:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0008_positions'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trade',
            name='date',
            field=models.DateField(auto_now=True),
        ),
    ]
