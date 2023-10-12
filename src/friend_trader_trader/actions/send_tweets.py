import tweepy
from django.conf import settings

from friend_trader_trader.models import FriendTechUser


class SendTweets:
    
    def __init__(self) -> None:
        self.t_client = tweepy.Client(
            consumer_key=settings.TWITTER_CONSUMER_KEY_1,
            consumer_secret=settings.TWITTER_CONSUMER_SECRET_1,
            access_token=settings.FRIEND_TRAD3R_ACCESS_TOKEN,
            access_token_secret=settings.FRIEND_TRAD3R_ACCESS_TOKEN_SECRET
        )

    @classmethod
    def run(self, *args, **kwargs):
        qs = FriendTechUser.objects.prefetch_related("share_prices", "trades").exclude(latest_price=None).order_by("-latest_price__price").values_list("twitter_username", "latest_price__price")[0:10]
        msg_header = "Top 10 user rankings \n"
        msg_body = "\n".join(
            f"{idx+1}. {twitter_username}: {latest_price}"
            for idx, (twitter_username, latest_price) in enumerate(qs)
        )
        msg_footer = "visit https://friendtrader.tech for more details \n"
        msg_tags = ", ".join([f"#{twitter_user[0]}" for twitter_user in qs])

        msg = msg_header + msg_body + msg_footer + msg_tags

        self.t_client.create_tweet(text=msg)
        return msg
