from rest_framework import serializers

from friend_trader_trader.models import Price


class PriceSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Price
        fields = "__all__"



class PriceSerializerTrade(serializers.ModelSerializer):

    is_buy = serializers.BooleanField(source="trade.is_buy", read_only=True)
    
    class Meta:
        model = Price
        fields = "__all__"