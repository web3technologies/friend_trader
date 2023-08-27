from celery import shared_task
from .base import BaseCeleryTask
from .block_actions import BlockActions


@shared_task(bind=True, name="perform_block_actions_task", base=BaseCeleryTask)
def perform_block_actions_task(self, block_hash):
    return BlockActions().run(block_hash)