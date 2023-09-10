from rest_framework import serializers

from friend_trader_trader.models import Trade
from friend_trader_trader.serializers import FriendTechUserMinimalSerializer
from friend_trader_trader.serializers.block import BlockMinimalSerializer


class TradeListSerializer(serializers.ModelSerializer):
    
    trader = FriendTechUserMinimalSerializer(read_only=True)
    block = BlockMinimalSerializer(read_only=True)
    
    class Meta:
        model = Trade
        fields = ["trader", "is_buy", "share_amount", "price", "hash", "block"]