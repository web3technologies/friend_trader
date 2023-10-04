
import time as Time

from django.conf import settings
from django.db import models
from django.db.utils import DatabaseError
from requests import Timeout
import tweepy
import random

from friend_trader_core.clients import kossetto_client
from friend_trader_core.utils import convert_to_central_time


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
    latest_price = models.OneToOneField("Price", default=None, null=True, related_name="latest_price", on_delete=models.CASCADE)
    
    tweepy_choices = [
        tweepy.OAuth1UserHandler(
            consumer_key=settings.TWITTER_CONSUMER_KEY_1,
            consumer_secret=settings.TWITTER_CONSUMER_SECRET_1,
            access_token=settings.TWITTER_ACCESS_TOKEN_1,
            access_token_secret=settings.TWITTER_ACCESS_TOKEN_SECRET_1
        ),
        tweepy.OAuth1UserHandler(
            consumer_key=settings.TWITTER_CONSUMER_KEY_2,
            consumer_secret=settings.TWITTER_CONSUMER_SECRET_2,
            access_token=settings.TWITTER_ACCESS_TOKEN_2,
            access_token_secret=settings.TWITTER_ACCESS_TOKEN_SECRET_2
        )
    ]
    
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
        tweepy_client = tweepy.API(random.choice(self.tweepy_choices))
        # if tweepy_client.rate_limit_status()["resources"].get("users")["/users/:id"].get("remaining") > 0:
        twitter_user_data = tweepy_client.get_user(screen_name=self.twitter_username)
        if twitter_user_data:
            self.twitter_followers = twitter_user_data.followers_count
            self.twitter_profile_pic = twitter_user_data.profile_image_url_https
            self.twitter_profile_banner = twitter_user_data.profile_banner_url if hasattr(twitter_user_data, "profile_banner_url") else None
            if auto_save:
                self.save(update_fields=["twitter_followers", "twitter_profile_pic", "twitter_profile_banner"])
        return self
    
    def update_latest_price(self, auto_save=True):
        from friend_trader_trader.models import Price
        last_price = Price.objects.filter(trade__subject=self).order_by("trade__block__block_timestamp").last()
        self.latest_price = last_price
        if auto_save:
            self.save(update_fields=["latest_price"])
        return self
    

    
    def get_candlestick_data(self, interval):
        from friend_trader_trader.models.price import Price
              
        data = Price.objects.filter(
                trade__subject=self
            ).annotate(
                block_timestamp=models.F('trade__block__block_timestamp')
            ).values('price', 'block_timestamp').order_by('block_timestamp')
        if not data:
            return []

        time = (data[0]['block_timestamp'] // interval) * interval
        end_time = time + interval

        candlesticks = []
        last_known_price = data[0]['price'].normalize()
        current_candle = {
            'open': last_known_price,
            'close': last_known_price,
            'high': last_known_price,
            'low': last_known_price,
            'time': convert_to_central_time(time),
            # 'End_Time': convert_to_central_time(end_time)
        }

        for entry in data:
            time_stamp, price = entry['block_timestamp'], entry['price']
            price = price.normalize()
            # check if current time is within the current candle stick defined by end_time
            while time_stamp >= end_time:
                candlesticks.append(current_candle)

                # essentially produce another candle and extend the time to the next candle
                # eventually the timestamp will be less than the end time
                time = end_time
                end_time = time + interval
                current_candle = {
                    'open': last_known_price,
                    'close': last_known_price,
                    'high': last_known_price,
                    'low': last_known_price,
                    'time': convert_to_central_time(time),
                    # 'End_Time': convert_to_central_time(end_time)
                }

            current_candle['close'] = price
            current_candle['high'] = max(current_candle['high'], price)
            current_candle['low'] = min(current_candle['low'], price)
            last_known_price = price

        candlesticks.append(current_candle)

        current_unix_time = int(Time.time())
        while end_time <= current_unix_time:
            time = end_time
            end_time = time + interval
            current_candle = {
                'open': last_known_price,
                'close': last_known_price,
                'high': last_known_price,
                'low': last_known_price,
                'time': convert_to_central_time(time),
                # 'End_Time': convert_to_central_time(end_time)
            }
            candlesticks.append(current_candle)

        return candlesticks