from django.db import models
from django.db.utils import DatabaseError
from friend_trader_core.clients import kossetto_client
from requests import Timeout


class FriendTechUser(models.Model):
    
    address = models.CharField(max_length=255, unique=True)
    
    twitter_username = models.CharField(max_length=255, null=True, default=None)
    twitter_profile_pic = models.CharField(max_length=255, null=True, default=None)
    twitter_followers = models.IntegerField(null=True, default=None)
    shares_supply = models.IntegerField(null=True, default=None)
    last_online = models.BigIntegerField(null=True, default=None)
    
    def __str__(self) -> str:
        return f"{self.twitter_username}"


    def get_kossetto_data(self, auto_save=True):
        try:
            kossetto_data = kossetto_client.get_kossetto_user(address=self.address)
            twitter_username = kossetto_data.get("twitterUsername")
            last_online = kossetto_data.get("lastOnline")
            self.twitter_username=twitter_username
            self.last_online = last_online
            if auto_save:
                self.save(update_fields=["twitter_username", "last_online"])
            return self
        except Timeout as e:
            print("handle timeout logic")
        except DatabaseError as e:
            print(self.address, self.twitter_username, self.twitter_profile_pic, self.last_online)
            raise(e)
        