import tweepy
from decouple import config

CONSUMER_KEY = config("TWITTER_CONSUMER_KEY_1")
CONSUMER_SECRET = config("TWITTER_CONSUMER_SECRET_1")
ACCESS_TOKEN = config("FRIEND_TRAD3R_ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = config("FRIEND_TRAD3R_ACCESS_TOKEN_SECRET")

t_client = tweepy.Client(consumer_key=CONSUMER_KEY,consumer_secret=CONSUMER_SECRET,access_token=ACCESS_TOKEN,access_token_secret=ACCESS_TOKEN_SECRET)
t_client.create_tweet(text="TESTING TWEET #testings")

