# Generated by Django 4.1.5 on 2023-02-03 10:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0041_alter_portfolio_inception_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='portgroup',
            name='type',
            field=models.CharField(default='', max_length=30),
        ),
    ]
