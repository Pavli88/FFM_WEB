# Generated by Django 4.2 on 2023-04-12 17:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0048_transaction_is_active'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction',
            name='security_id',
        ),
        migrations.AddField(
            model_name='transaction',
            name='security',
            field=models.CharField(default='', max_length=30),
        ),
    ]
