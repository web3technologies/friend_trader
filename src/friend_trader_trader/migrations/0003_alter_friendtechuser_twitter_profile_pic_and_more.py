# Generated by Django 4.2.4 on 2023-08-30 02:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('friend_trader_trader', '0002_alter_friendtechuser_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='friendtechuser',
            name='twitter_profile_pic',
            field=models.CharField(default=None, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='friendtechuser',
            name='twitter_username',
            field=models.CharField(default=None, max_length=255, null=True),
        ),
    ]
