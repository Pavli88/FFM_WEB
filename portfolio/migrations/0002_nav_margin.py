# Generated by Django 3.2.7 on 2024-10-17 21:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='nav',
            name='margin',
            field=models.FloatField(default=0.0),
        ),
    ]
