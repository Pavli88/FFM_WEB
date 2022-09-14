# Generated by Django 3.2.7 on 2022-08-17 19:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('instrument', '0005_auto_20210824_1350'),
    ]

    operations = [
        migrations.AddField(
            model_name='instruments',
            name='instrument_sub_type',
            field=models.CharField(default='', max_length=30),
        ),
        migrations.AddField(
            model_name='instruments',
            name='source_code',
            field=models.CharField(default='', max_length=30),
        ),
        migrations.AlterField(
            model_name='instruments',
            name='inst_code',
            field=models.CharField(max_length=30, unique=True),
        ),
    ]