from django.db import models
from django.utils import timezone

from friend_trader_trader.models import Block


class ShareTransactionBase:

    price = models.DecimalField(decimal_places=25, max_digits=40)
    block = models.ForeignKey(Block, on_delete=models.DO_NOTHING)
    transaction_timestamp = models.BigIntegerField()
    date_created = models.DateTimeField(default=timezone.now)