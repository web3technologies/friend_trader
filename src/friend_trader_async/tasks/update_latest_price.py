from django.db import transaction
import logging

from celery import shared_task
from friend_trader_trader.models import FriendTechUser

logger = logging.getLogger(__name__)

@shared_task(
    bind=False, 
    name="update_latest_price_task"
    )
def update_latest_price_task(users_ids:list):
    for user_id in users_ids:
        with transaction.atomic():
            friend_tech_user = FriendTechUser.objects.select_for_update().get(id=user_id)
            friend_tech_user.update_latest_price()
            logger.info(f"updating user latest price {friend_tech_user.twitter_username} {friend_tech_user.latest_price.trade.block.block_timestamp} {friend_tech_user.latest_price.price}")
    return users_ids
    