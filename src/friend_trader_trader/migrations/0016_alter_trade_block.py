# Generated by Django 4.2.4 on 2023-09-09 16:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('friend_trader_trader', '0015_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trade',
            name='block',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='friend_trader_trader.block'),
        ),
    ]