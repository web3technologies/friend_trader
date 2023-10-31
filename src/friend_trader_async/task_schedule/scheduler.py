from django.conf import settings

from friend_trader_async.celery import app as celery_app

from friend_trader_async.task_schedule.sheduler_manager import TaskScheduleManager


@celery_app.on_after_finalize.connect
def setup_task_scheduler(sender, **kwargs):
    manager = TaskScheduleManager()
    manager.delete_old_tasks()
    manager.create_scheduled_task(
        "cache_paginated_data_task", 
        "every_ten_minutes",
        enabled='YES'
    )
    manager.create_scheduled_task(
        "send_tweets_task",
        "hourly",
        enabled="YES"
    )