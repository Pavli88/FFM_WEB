# Generated by Django 3.0.5 on 2020-10-14 20:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0012_remove_positions_sec_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='positions',
            name='date',
            field=models.DateField(),
        ),
    ]
