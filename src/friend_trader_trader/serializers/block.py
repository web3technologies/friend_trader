from rest_framework import serializers

from friend_trader_trader.models import Block


class BlockMinimalSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Block
        fields = ("block_timestamp", "block_hash")