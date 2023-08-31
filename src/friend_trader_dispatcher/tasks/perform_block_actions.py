from celery import shared_task
from .base import BaseCeleryTask
from friend_trader_trader.actions.block_actions import BlockActions
from web3.exceptions import BlockNotFound


@shared_task(
    bind=True, 
    name="perform_block_actions_task", 
    base=BaseCeleryTask,
    autoretry_for=(BlockNotFound, ),
    retry_backoff=15,
    max_retries=3
    )
def perform_block_actions_task(self, block_hash):
    return BlockActions(task=self, block_hash=block_hash).run()