import random
import tweepy

from friend_trader_trader.models import FriendTechUser


class SendTweets:

    @classmethod
    def run(self, *args, **kwargs):
        ...
        qs = FriendTechUser.objects.prefetch_related("share_prices", "trades").exclude(latest_price=None).order_by("-latest_price__price").values_list("twitter_username", "latest_price__price")[0:10]
        tweepy_client = tweepy_client = tweepy.API(random.choice(FriendTechUser.tweepy_choices))
        msg_header = "Top 10 user rankings \n"
        msg_body = "\n".join(
            f"{idx+1}. {twitter_username}: {latest_price}"
            for idx, (twitter_username, latest_price) in enumerate(qs)
        )
        msg_footer = "visit https://friendtrader.tech for more details \n"
        msg_tags = ", ".join([f"#{twitter_user[0]}" for twitter_user in qs])

        msg = msg_header + msg_body + msg_footer + msg_tags

        tweepy_client.send_tweet(msg)
        return msg
