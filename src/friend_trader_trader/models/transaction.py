from django.db import models

from friend_trader_trader.models import Block, FriendTechUser


class Transaction(models.Model):
    
    type = models.CharField(choices=(("BUY", "BUY"), ("SELL", "SELL")), max_length=20)
    price = models.DecimalField(max_digits=45, decimal_places=20)
    transaction_hash = models.CharField(max_length=100)

    buyer = models.ForeignKey(FriendTechUser, on_delete=models.DO_NOTHING, related_name="buys")
    seller = models.ForeignKey(FriendTechUser, on_delete=models.DO_NOTHING, related_name="sells")
    block = models.ForeignKey(Block, on_delete=models.DO_NOTHING)