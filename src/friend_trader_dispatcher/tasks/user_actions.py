from celery import shared_task
from .base import BaseCeleryTask
from requests import HTTPError

from friend_trader_trader.models import FriendTechUser


@shared_task(
    bind=True, 
    name="retrieve_users_data_task", 
    base=BaseCeleryTask,
    # autoretry_for=(, ),
    retry_backoff=15,
    max_retries=3
    )
def retrieve_users_data_task(self, friend_tech_user_data:list):
    ## maybe call this recursively??? to handle retry or twitter failures??
    users_to_update = []
    for friend_tech_user in friend_tech_user_data:
        f_user = FriendTechUser.objects.get(address=friend_tech_user.get("address"))
        try:
            f_user.get_kossetto_data(auto_save=False)
            users_to_update.append(f_user)
        except HTTPError as e:
            return f"{self.address} not found in kossetto"
    FriendTechUser.objects.bulk_update(users_to_update, fields=["twitter_username", "twitter_profile_pic"])
    return friend_tech_user_data