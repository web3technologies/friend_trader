from celery import shared_task
from friend_trader_trader.models import FriendTechUser


@shared_task(
    bind=False, 
    name="update_latest_price_task"
    )
def update_latest_price_task(users_ids:list):
    for friend_tech_user in FriendTechUser.objects.filter(id__in=users_ids):
        friend_tech_user.update_latest_price()
    return users_ids
    