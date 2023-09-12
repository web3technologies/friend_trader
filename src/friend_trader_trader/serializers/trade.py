from rest_framework import serializers

from friend_trader_trader.models import Trade
from friend_trader_trader.serializers import FriendTechUserMinimalSerializer
from friend_trader_trader.serializers.block import BlockMinimalSerializer
from friend_trader_trader.serializers.price import PriceSerializer


class TradeListSerializer(serializers.ModelSerializer):
    
    trader = FriendTechUserMinimalSerializer(read_only=True)
    block = BlockMinimalSerializer(read_only=True)
    
    class Meta:
        model = Trade
        fields = ["trader", "is_buy", "share_amount", "price", "hash", "block"]
        


class TradeSerializer(serializers.ModelSerializer):
    
    prices = PriceSerializer(many=True, read_only=True)
    trader = FriendTechUserMinimalSerializer(read_only=True)
    subject = FriendTechUserMinimalSerializer(read_only=True)
    
    
    class Meta:
        model = Trade
        fields = "__all__"