from celery import shared_task, chain, group

from friend_trader_async.tasks.perform_block_actions import  perform_block_actions_task
from friend_trader_async.tasks.user_actions import retrieve_users_data_task
from friend_trader_async.tasks.update_latest_price import update_latest_price_task


@shared_task(bind=False, name="chained_block_actions_task")
def chained_block_actions_task(block_number=None):
    return chain(
        perform_block_actions_task.s(block_number=block_number), 
        dispatch_to_grouped_tasks.s()
    ).apply_async()
    
    
@shared_task(bind=False, name="dispatch_to_grouped_tasks")
def dispatch_to_grouped_tasks(user_id_result):
    tasks_to_run = [
        retrieve_users_data_task.s(user_id_result),
        update_latest_price_task.s(user_id_result)
    ]
    group(tasks_to_run).apply_async()
    return user_id_result