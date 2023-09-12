from rest_framework import serializers

from friend_trader_trader.models import Price


class PriceSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Price
        fields = "__all__"