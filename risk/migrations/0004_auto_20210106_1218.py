# Generated by Django 3.0.5 on 2021-01-06 11:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('risk', '0003_auto_20200522_1609'),
    ]

    operations = [
        migrations.RenameField(
            model_name='robotrisk',
            old_name='in_exp',
            new_name='daily_risk_perc',
        ),
        migrations.RemoveField(
            model_name='robotrisk',
            name='m_dd',
        ),
        migrations.RemoveField(
            model_name='robotrisk',
            name='p_level',
        ),
        migrations.RemoveField(
            model_name='robotrisk',
            name='quantity',
        ),
        migrations.RemoveField(
            model_name='robotrisk',
            name='sl_policy',
        ),
    ]
