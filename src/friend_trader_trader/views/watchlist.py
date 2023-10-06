from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from friend_trader_core.mixins import ThrottleMixin
from friend_trader_trader.models import FriendTechUserWatchList
from friend_trader_trader.serializers import FriendTechUserWatchListSeriazlier



class FriendTechUserWatchListViewset(ModelViewSet, ThrottleMixin):
    
    queryset = FriendTechUserWatchList.objects.all()
    serializer_class = FriendTechUserWatchListSeriazlier
    permission_classes = [ IsAuthenticated ]
    
    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

