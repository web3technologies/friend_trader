from celery import shared_task, chain

from friend_trader_dispatcher.tasks.perform_block_actions import  perform_block_actions_task
from friend_trader_dispatcher.tasks.user_actions import retrieve_users_data_task

@shared_task(
    bind=False, 
    name="chained_block_actions_task"
    )
def chained_block_actions_task(block_number=None):
    return chain(perform_block_actions_task.s(block_number=block_number), retrieve_users_data_task.s()).apply_async()