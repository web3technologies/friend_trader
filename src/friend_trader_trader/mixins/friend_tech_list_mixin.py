from django.core.paginator import Paginator, EmptyPage

from friend_trader_trader.models import FriendTechUser
from friend_trader_trader.serializers import FriendTechUserListLatestPriceSerializer


def get_paginated_data_for_page(page):
    queryset = FriendTechUser.objects.exclude(latest_price=None).order_by("-latest_price__price", "id").distinct("latest_price__price", "id")
    
    paginator = Paginator(queryset, 50) 
    paginated_queryset = paginator.page(page)
    
    try:
        current_page = paginator.page(page)
    except EmptyPage:
        current_page = paginator.page(paginator.num_pages) 

    serializer = FriendTechUserListLatestPriceSerializer(paginated_queryset, many=True)
    
    pagination_data = {
        'next': current_page.next_page_number() if current_page.has_next() else None,
        'previous': current_page.previous_page_number() if current_page.has_previous() else None,
        'count': paginator.count,
        'results': serializer.data
    }
    return pagination_data