from django.db import models

from friend_trader_core.clients import kossetto_client
from requests import Timeout


class FriendTechUser(models.Model):
    
    address = models.CharField(max_length=255, unique=True)
    
    twitter_username = models.CharField(max_length=255, null=True, default=None)
    twitter_profile_pic = models.CharField(max_length=255, null=True, default=None)
    twitter_followers = models.IntegerField(null=True, default=None)
    share_count = models.IntegerField(null=True, default=None)
    
    def __str__(self) -> str:
        return self.twitter_username


    def get_kossetto_data(self, auto_save=True):
        try:
            kossetto_data = kossetto_client.get_kossetto_user(address=self.address)
            twitter_username = kossetto_data.get("twitterUsername")
            profile_pic_url = kossetto_data.get("twitterPfpUrl")
            self.twitter_username=twitter_username
            self.twitter_profile_pic=profile_pic_url
            if auto_save:
                self.save(update_fields=["twitter_username", "twitter_profile_pic"])
            return self
        except Timeout as e:
            print("handle timeout logic")
        