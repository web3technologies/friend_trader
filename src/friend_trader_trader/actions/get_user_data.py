from tweepy.errors import NotFound as TwitterUserNotFound, TweepyException
from django.conf import settings
import requests
import tweepy

from friend_trader_trader.models import FriendTechUser
from friend_trader_trader.exceptions.exceptions import TwitterForbiddenException



class GetUserData:
    
    twitter_auth = tweepy.OAuth1UserHandler(
            consumer_key=settings.TWITTER_CONSUMER_KEY,
            consumer_secret=settings.TWITTER_CONSUMER_SECRET,
            access_token=settings.TWITTER_ACCESS_TOKEN,
            access_token_secret=settings.TWITTER_ACCESS_TOKEN_SECRET
        )
    tweepy_client = tweepy.API(twitter_auth)
    
    
    def __init__(self) -> None:
        self.twitter_userdata = []
        self.notification_data =  []
    
    
    def __manage_twitter_user_data(self, friend_tech_user):
        try:
            twitter_user_data = self.tweepy_client.get_user(screen_name=friend_tech_user.twitter_username)
            if twitter_user_data:
                friend_tech_user.twitter_followers = twitter_user_data.followers_count
                friend_tech_user.twitter_profile_pic = twitter_user_data.profile_image_url_https
                friend_tech_user.save(update_fields=["twitter_followers", "twitter_profile_pic"])
                if twitter_user_data.followers_count >= 100_000:
                    share_price = friend_tech_user.share_prices.all().order_by("block__block_number").last()
                    msg = f"TwitterName: {friend_tech_user.twitter_username}, Followers: {twitter_user_data.followers_count}, Following: {twitter_user_data.friends_count}, Last Price: Ξ{str(share_price.price.normalize()) if share_price else ''}, Total Shares: {friend_tech_user.shares_supply}"
                    print(msg)
                    self.twitter_userdata.append(msg)
                    self.notification_data.append({
                        "msg": msg,
                        "image_url": friend_tech_user.twitter_profile_pic,
                        "twitter_name": friend_tech_user.twitter_username,
                        "shares_count": friend_tech_user.shares_supply
                    })
                else:
                    print(f"Not enough followers: {friend_tech_user.twitter_username}")
        except TwitterUserNotFound as e:
            print(f"{friend_tech_user.twitter_username} not found")
        except TweepyException as e:
            if 63 in e.api_codes:
                raise TwitterForbiddenException("403 forbidden from twitter client")
            else:
                raise e
           
            
    def __handle_notifications(self):
        for notification in self.notification_data:
            if notification["shares_count"] < 3:
                self.__send_discord_messages(notification, settings.DISCORD_WEBHOOK_NEW_USER_GREATER_THAN_100K)
            else:
                self.__send_discord_messages(notification, settings.DISCORD_WEBHOOK)
                    
                    
    def __send_discord_messages(self, notification, webhook_url):
        embed = {
            "title": notification['twitter_name'],
            "url": f"https://twitter.com/{notification['twitter_name']}",
            "description": notification["msg"],
            "color": 7506394,
            "thumbnail": {
                "url": notification["image_url"]
            }
        }
        payload = {
            "embeds": [embed]
        }
        response = requests.post(webhook_url, json=payload)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
        else:
            print(f"Payload delivered successfully, code {response.status_code}.")
    
    
    def run(self, users_ids:list):
        
        friend_tech_users = FriendTechUser.objects.prefetch_related("share_prices").filter(id__in=[user_id for user_id in users_ids])
        
        for friend_tech_user in friend_tech_users:
            if not friend_tech_user.twitter_username:
                try:
                    friend_tech_user.get_kossetto_data(auto_save=True)
                except requests.exceptions.HTTPError:
                    print(f"Error fetching data for user: {friend_tech_user}")
            
            if friend_tech_user.twitter_username:
                self.__manage_twitter_user_data(friend_tech_user)
        self.__handle_notifications()
        
        return len(self.notification_data)