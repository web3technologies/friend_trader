from django.db import models

from friend_trader_trader.models import FriendTechUser


class SharePrice(models.Model):
    
    current_price = models.DecimalField(max_digits=45, decimal_places=20)
    friend_tech_user = models.ForeignKey(FriendTechUser, on_delete=models.DO_NOTHING, related_name="share_prices")
