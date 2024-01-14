from celery import shared_task

from friend_trader_trader.actions.send_tweets import SendTweets



@shared_task(bind=False, name="send_tweets_task")
def send_tweets_task(*args, **kwargs):
    return SendTweets.run()