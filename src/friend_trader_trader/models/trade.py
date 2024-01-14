from django.db import models

from friend_trader_trader.models import Block, FriendTechUser


class Trade(models.Model):
    
    subject = models.ForeignKey(FriendTechUser, on_delete=models.CASCADE, related_name="share_prices")
    trader = models.ForeignKey(FriendTechUser, on_delete=models.CASCADE, related_name="trades")
    is_buy = models.BooleanField(default=False)
    share_amount = models.IntegerField()
    price = models.DecimalField(max_digits=45, decimal_places=20)
    protocol_fee = models.DecimalField(max_digits=45, decimal_places=20, null=True, default=None)
    subject_fee = models.DecimalField(max_digits=45, decimal_places=20, null=True, default=None)
    supply = models.IntegerField()
    
    hash = models.CharField(max_length=100, unique=True) # handle unique case so duplicate trades are not stored
    block = models.ForeignKey(Block, on_delete=models.CASCADE)