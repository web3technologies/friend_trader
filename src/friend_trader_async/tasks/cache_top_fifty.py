from celery import shared_task
from django.core.cache import cache

from friend_trader_trader.models import FriendTechUser
from friend_trader_trader.serializers import FriendTechUserListLatestPriceSerializer
from django.core.cache import cache
from django.core.paginator import Paginator


CACHE_KEY_PATTERN = "paginated_data_page_{page}"


@shared_task
def cache_paginated_data(page):
    data = get_paginated_data_for_page(page)
    cache.set(CACHE_KEY_PATTERN.format(page=page), data, 60*15)


def get_paginated_data_for_page(page):
    queryset = FriendTechUser.objects.exclude(latest_price=None).order_by("-latest_price__price", "id").distinct("latest_price__price", "id")
    
    paginator = Paginator(queryset, 50) 
    paginated_queryset = paginator.page(page)

    serializer = FriendTechUserListLatestPriceSerializer(paginated_queryset, many=True)
    return serializer.data


def list(self, request, *args, **kwargs):
    page = request.GET.get('page', 1)
    data = cache.get(CACHE_KEY_PATTERN.format(page=page))
    
    if data is None:
        data = get_paginated_data_for_page(page)
        cache.set(CACHE_KEY_PATTERN.format(page=page), data, 60*15)
        
    return Response(data)

