from django.db import models

from friend_trader_trader.models import Block, FriendTechUser, Transaction


class SharePrice(models.Model):
    
    buy_price = models.DecimalField(max_digits=45, decimal_places=20, null=True, default=None)
    sell_price = models.DecimalField(max_digits=45, decimal_places=20, null=True, default=None)
    
    transaction = models.ForeignKey(Transaction, on_delete=models.DO_NOTHING, null=True, default=None)
    block = models.ForeignKey(Block, on_delete=models.DO_NOTHING, null=True, default=None)
    friend_tech_user = models.ForeignKey(FriendTechUser, on_delete=models.DO_NOTHING, related_name="share_prices")
