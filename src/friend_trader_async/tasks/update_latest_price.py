from celery import shared_task
from friend_trader_trader.models import FriendTechUser


@shared_task(
    bind=False, 
    name="update_latest_price_task"
    )
def update_latest_price_task(users_ids:list):
    friend_tech_users = FriendTechUser.objects.prefetch_related("share_prices", "share_prices__prices").filter(id__in=users_ids)
    for friend_tech_user in friend_tech_users:
        friend_tech_user.update_latest_price()
    return users_ids
    