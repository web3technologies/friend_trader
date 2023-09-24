from celery import shared_task
from friend_trader_trader.models import FriendTechUser


@shared_task(
    bind=False, 
    name="update_latest_price_task"
    )
def update_latest_price_task(users_ids:list):
    friend_tech_users = FriendTechUser.objects.prefetch_related("share_prices", "share_prices__prices").filter(id__in=users_ids)
    users_to_update = []
    for friend_tech_user in friend_tech_users:
        friend_tech_user.update_latest_price(auto_save=False)
        if friend_tech_user.latest_price:
            users_to_update.append(friend_tech_user)
    FriendTechUser.objects.bulk_update(users_to_update, fields=["latest_price"])
    return users_ids
    