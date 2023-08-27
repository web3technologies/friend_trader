import logging
from celery import Task
from celery.utils.log import get_task_logger


class BaseCeleryTask(Task):

    def __init__(self) -> None:
        super().__init__()
        self.logger = logging.LoggerAdapter(get_task_logger(self.name), extra={"className": self.__class__.__name__})

        def on_success(self, *args, **kwargs):

            self.logger.info("Task %s was successful", self.name)
        
        def on_failure(self, *args, **kwargs):
            self.logger.error("Task %s has failed", self.name)