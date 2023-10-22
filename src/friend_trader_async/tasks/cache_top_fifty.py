from celery import shared_task

from django.core.cache import cache
from django.conf import settings

from friend_trader_trader.mixins.friend_tech_list_mixin import get_paginated_data_for_page



@shared_task(bind=False, name="cache_paginated_data_task")
def cache_paginated_data_task(page):
    data = get_paginated_data_for_page(page)
    cache.set(settings.FRIEND_TECH_USER_LIST_CACHE_KEY_PATTERN.format(page=page), data, 60*15)
