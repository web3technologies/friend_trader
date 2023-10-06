from django.conf import settings
from django.db import models
from django.utils import timezone

from friend_trader_trader.models import FriendTechUser


class FriendTechUserWatchList(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    friend_tech_user = models.ForeignKey(FriendTechUser, on_delete=models.CASCADE)
    date_added = models.DateTimeField(default=timezone.now)



