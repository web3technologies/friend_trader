from rest_framework import serializers

from friend_trader_trader.models import FriendTechUser


class FriendTechUserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = FriendTechUser
        fields = "__all__"
