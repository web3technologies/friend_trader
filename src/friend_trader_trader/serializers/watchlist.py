from rest_framework import serializers

from friend_trader_trader.models import FriendTechUserWatchList
from friend_trader_trader.serializers.friend_tech_user import FriendTechUserListLatestPriceSerializer


class FriendTechUserWatchListSeriazlier(serializers.ModelSerializer):
    
    friend_tech_user = FriendTechUserListLatestPriceSerializer(read_only=True)
    
    class Meta:
        model = FriendTechUserWatchList
        fields = "__all__"
        
        
class FriendTechUserWatchListSeriazlierCreate(serializers.ModelSerializer):
    
    class Meta:
        model = FriendTechUserWatchList
        fields = "__all__"