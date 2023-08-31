from django.db import models

from friend_trader_trader.models import FriendTechUser
from friend_trader_trader.models.share_transaction_base import ShareTransactionBase


class ShareBuy(models.Model, ShareTransactionBase):

    buyer = models.ForeignKey(FriendTechUser, on_delete=models.DO_NOTHING)