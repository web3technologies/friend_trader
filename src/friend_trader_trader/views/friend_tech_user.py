from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import NotFound

from friend_trader_trader.models import FriendTechUser
from friend_trader_trader.serializers import FriendTechUserCandleStickSerializer


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