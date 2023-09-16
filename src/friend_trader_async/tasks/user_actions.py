from celery import shared_task
from .base import BaseCeleryTask

from friend_trader_trader.actions.get_user_data import GetUserData


@shared_task(
    bind=True, 
    name="retrieve_users_data_task", 
    base=BaseCeleryTask,
    # autoretry_for=(, ),
    retry_backoff=15,
    max_retries=3
    )
def retrieve_users_data_task(self, users_ids:list):
    return GetUserData().run(users_ids=users_ids)