import logging
from decouple import config

from django_celery_beat.models import CrontabSchedule, PeriodicTask

logger = logging.getLogger(__name__)


class TaskScheduleManager:

    periodic_crons = {}

    def __init__(self) -> None:
        self.periodic_crons["minutely"], _ = CrontabSchedule.objects.get_or_create(
            minute="*", hour="*", day_of_week="*", day_of_month="*", month_of_year="*"
        )
        self.periodic_crons["every_fifteen_minutes"], _ = CrontabSchedule.objects.get_or_create(
            minute="*/15", hour="*", day_of_week="*", day_of_month="*", month_of_year="*"
        )
        self.periodic_crons["every_ten_minutes"], _ = CrontabSchedule.objects.get_or_create(
            minute="*/10", hour="*", day_of_week="*", day_of_month="*", month_of_year="*"
        )
        self.periodic_crons["hourly"], _ = CrontabSchedule.objects.get_or_create(
            minute="0", hour="*", day_of_week="*", day_of_month="*", month_of_year="*"
        )
        self.periodic_crons["monthly"], _ = CrontabSchedule.objects.get_or_create(
            minute="0", hour="0", day_of_week="*", day_of_month="1", month_of_year="*"
        )

    def _create_or_update_schedule(self, name, task, crontab, priority, expire_seconds, enabled):
        
        try:
            periodic_task = PeriodicTask.objects.get(
                name=name, 
                task=task, 
                priority=priority, 
                expire_seconds=expire_seconds
                )
        except PeriodicTask.DoesNotExist:
            periodic_task = PeriodicTask.objects.create(
                name=name,
                task=task,
                crontab=crontab,
                priority=priority,
                expire_seconds=expire_seconds,
                last_run_at=None
            )
        else:
            periodic_task.last_run_at = None
        finally:
            periodic_task.enabled = True if enabled == "YES" and config("ENVIRONMENT") == "prod" else False
            periodic_task.save()

    def create_scheduled_task(self, task_name, periodic_name, enabled, priority=0, expire_seconds=30):
        if periodic_name not in self.periodic_crons:
            raise NotImplementedError(f"Cron {periodic_name} is not implemented.")
        
        self._create_or_update_schedule(
            f"{periodic_name}_{task_name}",
            task_name,
            self.periodic_crons[periodic_name],
            priority,
            expire_seconds,
            enabled
        )
    
    def delete_old_tasks(self):
        query = PeriodicTask.objects.all()
        objs_deleted = list(query.values())
        count_deleted, _ = query.delete()
        logger.info("Deletion of %d tasks.", count_deleted)
        if count_deleted:
            logger.info("\n".join([f"Task {obj['name']} deleted" for obj in objs_deleted]))