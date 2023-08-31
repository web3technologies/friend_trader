# Generated by Django 4.2.4 on 2023-08-30 23:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('friend_trader_trader', '0003_alter_friendtechuser_twitter_profile_pic_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Block',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('block_hash', models.CharField(max_length=255)),
                ('block_number', models.IntegerField(default=None, null=True)),
                ('block_timestamp', models.BigIntegerField(default=None, null=True)),
                ('date_sniffed', models.DateTimeField(default=None, null=True)),
            ],
        ),
    ]
