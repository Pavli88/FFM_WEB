# Generated by Django 3.0.5 on 2020-10-14 20:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0011_auto_20201014_2222'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='positions',
            name='sec_type',
        ),
    ]
