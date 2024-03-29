# Generated by Django 4.2.4 on 2023-08-31 04:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('friend_trader_trader', '0004_block'),
    ]

    operations = [
        migrations.AddField(
            model_name='friendtechuser',
            name='share_count',
            field=models.IntegerField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='friendtechuser',
            name='twitter_followers',
            field=models.IntegerField(default=None, null=True),
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('BUY', 'BUY'), ('SELL', 'SELL')], max_length=20)),
                ('price', models.DecimalField(decimal_places=20, max_digits=45)),
                ('timestamp', models.BigIntegerField()),
                ('transaction_hash', models.CharField(max_length=100)),
                ('block', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='friend_trader_trader.block')),
                ('buyer', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='buys', to='friend_trader_trader.friendtechuser')),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='sells', to='friend_trader_trader.friendtechuser')),
            ],
        ),
        migrations.CreateModel(
            name='SharePrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('current_price', models.DecimalField(decimal_places=20, max_digits=45)),
                ('friend_tech_user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='share_prices', to='friend_trader_trader.friendtechuser')),
            ],
        ),
    ]
