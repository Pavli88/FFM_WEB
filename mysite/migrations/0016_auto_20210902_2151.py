# Generated by Django 3.2.7 on 2021-09-02 19:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mysite', '0015_processinfo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='processinfo',
            name='pid',
        ),
        migrations.RemoveField(
            model_name='processinfo',
            name='status',
        ),
    ]