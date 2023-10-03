from django.db.models import Count
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.throttling import AnonRateThrottle

from friend_trader_trader.models import FriendTechUser
from friend_trader_trader.serializers import FriendTechUserCandleStickSerializer, FriendTechUserListSerializer, FriendTechUserListLatestPriceSerializer
from friend_trader_trader.pagination.fifty_items import FiftyItemsPagination


class FriendTechUserViewSet(ModelViewSet):
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
    
    
    # @method_decorator(cache_page(60*15), name="dispatch")
    def list(self, request, *args, **kwargs):
        pagination_class = FiftyItemsPagination()
        
        paginated_queryset = pagination_class.paginate_queryset(
            queryset=self.queryset.exclude(latest_price=None).order_by("-latest_price__price"), 
            request=request, 
            view=self
        )
        
        if paginated_queryset is not None:
            serializer = self.get_serializer_class()(paginated_queryset, many=True)
            return pagination_class.get_paginated_response(serializer.data)

        serializer = self.get_serializer_class()(self.queryset, many=True)
        return Response(serializer.data)
    
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
    

class FriendTechUserListView(APIView):
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
        