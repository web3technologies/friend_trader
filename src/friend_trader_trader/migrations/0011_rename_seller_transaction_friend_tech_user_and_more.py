# Generated by Django 4.2.4 on 2023-09-04 02:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('friend_trader_trader', '0010_alter_transaction_type'),
    ]

    operations = [
        migrations.RenameField(
            model_name='transaction',
            old_name='seller',
            new_name='friend_tech_user',
        ),
        migrations.RenameField(
            model_name='transaction',
            old_name='buyer',
            new_name='tx_from',
        ),
    ]