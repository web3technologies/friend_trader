from django.conf import settings
from django.db import models
from django.db.utils import DatabaseError
from friend_trader_core.clients import kossetto_client
from requests import Timeout
import tweepy


class FriendTechUser(models.Model):
    
    address = models.CharField(max_length=255, unique=True)
    
    twitter_username = models.CharField(max_length=255, null=True, default=None)
    twitter_profile_pic = models.CharField(max_length=255, null=True, default=None)
    twitter_profile_banner = models.CharField(max_length=255, null=True, default=None)
    twitter_followers = models.IntegerField(null=True, default=None)
    verified = models.BooleanField(default=False)
    shares_supply = models.IntegerField(null=True, default=None)
    holder_count = models.IntegerField(null=True, default=None)
    holding_count = models.IntegerField(null=True, default=None)
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
            self.shares_supply = kossetto_data.get("shareSupply")
            self.holder_count = kossetto_data.get("holderCount")
            self.holding_count = kossetto_data.get("holdingCount")
            if auto_save:
                self.save(update_fields=["twitter_username", "last_online", "shares_supply", "holder_count", "holding_count"])
            return self
        except Timeout as e:
            print("handle timeout logic")
            return self
        except DatabaseError as e:
            print(self.address, self.twitter_username, self.twitter_profile_pic, self.last_online)
            raise(e)
        
    def get_twitter_data(self, auto_save=True):
        twitter_auth = tweepy.OAuth1UserHandler(
            consumer_key=settings.TWITTER_CONSUMER_KEY,
            consumer_secret=settings.TWITTER_CONSUMER_SECRET,
            access_token=settings.TWITTER_ACCESS_TOKEN,
            access_token_secret=settings.TWITTER_ACCESS_TOKEN_SECRET
        )
        tweepy_client = tweepy.API(twitter_auth)
        twitter_user_data = tweepy_client.get_user(screen_name=self.twitter_username)
        if twitter_user_data:
            self.twitter_followers = twitter_user_data.followers_count
            self.twitter_profile_pic = twitter_user_data.profile_image_url_https
            self.twitter_profile_banner = twitter_user_data.profile_banner_url if hasattr(twitter_user_data, "profile_banner_url") else None
            if auto_save:
                self.save(update_fields=["twitter_followers", "twitter_profile_pic", "twitter_profile_banner"])
        return self