from django.db.models import F, Count

from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from friend_trader_trader.models import FriendTechUser
from friend_trader_trader.serializers import FriendTechUserCandleStickSerializer, FriendTechUserListSerializer


class FriendTechUserViewSet(ModelViewSet):
    queryset = FriendTechUser.objects.prefetch_related("share_prices", "trades").all()
    serializer_class = FriendTechUserCandleStickSerializer
    lookup_field = "twitter_username"
    default_interval = 3600
    
    def list(self, *args, **kwargs):
        raise NotFound("Endpoint not available")
    
    def get_serializer_class(self):
        return super().get_serializer_class()
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        timeframe = self.request.query_params.get("interval", self.default_interval)
        context["interval"] = timeframe
        return context
    

class FriendTechUserListView(APIView):
    
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
        