# Generated by Django 3.2.7 on 2022-07-29 22:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0030_portfolioholdings'),
    ]

    operations = [
        migrations.AddField(
            model_name='nav',
            name='portfolio_code',
            field=models.CharField(default='', max_length=30),
        ),
    ]