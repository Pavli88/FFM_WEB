# Generated by Django 5.1.2 on 2025-02-27 22:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0002_portfolio_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='portfolio',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='portfolio.portfolio'),
        ),
    ]
