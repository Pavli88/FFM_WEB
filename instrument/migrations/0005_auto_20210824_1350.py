# Generated by Django 3.0.5 on 2021-08-24 11:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('instrument', '0004_auto_20210823_2154'),
    ]

    operations = [
        migrations.AlterField(
            model_name='prices',
            name='date',
            field=models.DateField(),
        ),
    ]
