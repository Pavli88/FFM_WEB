# Generated by Django 5.1.2 on 2025-03-06 15:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0003_transaction_portfolio'),
    ]

    operations = [
        migrations.RenameField(
            model_name='portfolio',
            old_name='is_automated',
            new_name='trading_allowed',
        ),
    ]
