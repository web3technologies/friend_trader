from rest_framework import serializers
from friend_trader_trader.serializers.trade import TradeSerializer

from friend_trader_trader.models import Block


class BlockDetailSerializer(serializers.ModelSerializer):
    
    trade_set = TradeSerializer(many=True, read_only=True)
    
    class Meta:
        model = Block
        fields = "__all__"