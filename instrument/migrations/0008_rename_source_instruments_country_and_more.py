# Generated by Django 4.1.5 on 2023-02-20 20:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('instrument', '0007_tickers'),
    ]

    operations = [
        migrations.RenameField(
            model_name='instruments',
            old_name='source',
            new_name='country',
        ),
        migrations.RemoveField(
            model_name='instruments',
            name='source_code',
        ),
    ]