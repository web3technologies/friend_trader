from django.conf import settings
from django.core.cache import cache
from django.db.models import Count

from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from friend_trader_core.mixins import ThrottleMixin
from friend_trader_trader.mixins.friend_tech_list_mixin import get_paginated_data_for_page
from friend_trader_trader.models import FriendTechUser
from friend_trader_trader.serializers import FriendTechUserCandleStickSerializer, FriendTechUserListSerializer, FriendTechUserListLatestPriceSerializer
from friend_trader_trader.pagination.fifty_items import FiftyItemsPagination



class FriendTechUserViewSet(ReadOnlyModelViewSet, ThrottleMixin):
    
    """
        List will return a list of users and some associated data. This is primarily used on the home page
        Retrieve  will return the detail of a user and the associated candlestick data. 
        It is used in the detail page of a user
    """

    queryset = FriendTechUser.objects.prefetch_related("share_prices", "trades").all()
    serializer_class = FriendTechUserCandleStickSerializer
    lookup_field = "twitter_username"
    default_interval = 3600
    http_method_names = ['get', 'head', 'options']
    throttle_classes = [AnonRateThrottle]
    
    def list(self, request, *args, **kwargs):
        page = request.GET.get('page', 1)
        data = cache.get(settings.FRIEND_TECH_USER_LIST_CACHE_KEY_PATTERN.format(page=page))
        
        if data is None:
            data = get_paginated_data_for_page(page)
            cache.set(settings.FRIEND_TECH_USER_LIST_CACHE_KEY_PATTERN.format(page=page), data, 60*10)
            
        return Response(data)
    
    def get_serializer_class(self):
        if self.action == "list":
            return FriendTechUserListLatestPriceSerializer
        if self.action == "retrieve":
            return FriendTechUserCandleStickSerializer
        return super().get_serializer_class()
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        timeframe = self.request.query_params.get("interval", self.default_interval)
        context["interval"] = timeframe
        return context
    

class FriendTechUserListView(APIView, ThrottleMixin):
    """
        This view will return the list of users
        It is primarily used in the lookup of users in the search bar
    """
    
    serializer_class = FriendTechUserListSerializer
    queryset = FriendTechUser.objects.annotate(
            is_null=Count('twitter_followers')
            ).order_by('-is_null', '-twitter_followers')
    
    def get(self, *args, **kwargs):
        twitter_username = self.request.query_params.get("twitterUsername", "")
        if twitter_username:
            users = self.queryset.filter(twitter_username__icontains=twitter_username)
            user_data = self.serializer_class(users, many=True)
            return Response(data=user_data.data[0:10], status=HTTP_200_OK)
        else:
            return Response(data=[], status=HTTP_200_OK)
        