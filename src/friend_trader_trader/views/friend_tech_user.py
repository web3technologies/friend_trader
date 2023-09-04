from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import NotFound

from friend_trader_trader.models import FriendTechUser
from friend_trader_trader.serializers import FriendTechUserSerializer


class FriendTechUserViewSet(ModelViewSet):
    queryset = FriendTechUser.objects.prefetch_related("share_prices", "trades").all()
    serializer_class = FriendTechUserSerializer    
    
        
    def list(self, *args, **kwargs):
        raise NotFound("Endpoint not available")