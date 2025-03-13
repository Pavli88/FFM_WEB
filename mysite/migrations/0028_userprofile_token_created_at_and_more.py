# Generated by Django 5.1.2 on 2025-03-06 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mysite', '0027_userprofile_delete_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='token_created_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='reset_token',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
