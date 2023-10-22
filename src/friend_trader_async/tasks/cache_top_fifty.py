from celery import shared_task

from django.core.cache import cache
from django.conf import settings

from friend_trader_trader.mixins.friend_tech_list_mixin import get_paginated_data_for_page



@shared_task(bind=False, name="cache_paginated_data_task")
def cache_paginated_data_task():
    for page_num in range(1,6):
        data = get_paginated_data_for_page(page_num)
        cache.set(settings.FRIEND_TECH_USER_LIST_CACHE_KEY_PATTERN.format(page=page_num), data, 60*10)
