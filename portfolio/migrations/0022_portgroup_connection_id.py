# Generated by Django 3.0.5 on 2021-01-28 17:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0021_portgroup'),
    ]

    operations = [
        migrations.AddField(
            model_name='portgroup',
            name='connection_id',
            field=models.CharField(default='', max_length=30, unique=True),
        ),
    ]
