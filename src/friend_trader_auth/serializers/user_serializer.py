from rest_framework import serializers
from friend_trader_auth.models import User


class FriendTraderUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = "__all__"