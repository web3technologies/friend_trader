import os
import logging

from celery import Celery
from celery.app.log import TaskFormatter
from celery.signals import after_setup_task_logger, after_task_publish

_logger = logging.getLogger(__name__)


os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'friend_trader.settings')

app = Celery("friend_trader_dispatcher")

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@after_task_publish.connect()
def log_for_task_publishment(sender=None, headers=None, body=None, **kwargs):
    info = headers if "task" in headers else body
    _logger.info("Triggered task %(name)s with id %(id)s", {"name": sender, "id": info["id"]})


@after_setup_task_logger.connect
def setup_task_logger(logger, *args, **kwargs):
    for handler in logger.handlers:
        handler.setFormatter(
            TaskFormatter(
                "[%(asctime)s: %(levelname)s/%(processName)s] %(task_name)s[%(task_id)s]: [%(className)s] %(messages)s"
            )
        )