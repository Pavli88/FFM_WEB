# Generated by Django 3.2.7 on 2021-10-01 12:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mysite', '0021_systemmessages_msg_sub_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='systemmessages',
            name='verified',
            field=models.BooleanField(default=False),
        ),
    ]
