
from rest_framework import serializers

from friend_trader_core.utils import convert_to_central_time
from friend_trader_trader.models import FriendTechUser
from friend_trader_trader.serializers.price import PriceSerializer


class FriendTechUserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = FriendTechUser
        fields = "__all__"
        
        
class FriendTechUserMinimalSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = FriendTechUser
        fields = ("twitter_username", "twitter_profile_pic")


class FriendTechUserListSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = FriendTechUser
        fields = ("twitter_username", "twitter_profile_pic", "twitter_followers")
        
class FriendTechUserListLatestPriceSerializer(serializers.ModelSerializer):
    
    latest_price = PriceSerializer(read_only=True)
    last_trade_time = serializers.SerializerMethodField("get_last_trade_time")
    
    class Meta:
        model = FriendTechUser
        fields = ("id", "twitter_username", "twitter_profile_pic", "twitter_followers", "latest_price", "shares_supply", "last_trade_time")
    
    def get_last_trade_time(self, obj, *args, **kwargs):
        if last_trade := obj.share_prices.select_related("block").order_by("block__block_timestamp").last():
            return last_trade.block.block_timestamp
        else:
            return None
    

class FriendTechUserCandleStickSerializer(FriendTechUserSerializer):
    
    
    candle_stick_data = serializers.SerializerMethodField("generate_candlestick")
    first_trade = serializers.SerializerMethodField("get_first_trade")
    last_trade = serializers.SerializerMethodField("get_last_trade")
    latest_price = serializers.SlugRelatedField(slug_field="price", read_only=True)
    
    def get_first_trade(self, obj):
        return convert_to_central_time(obj.share_prices.order_by("block__block_timestamp").first().block.block_timestamp)
    
    def get_last_trade(self, obj):
        return convert_to_central_time(obj.share_prices.order_by("block__block_timestamp").last().block.block_timestamp)
    
    def generate_candlestick(self, obj, *args, **kwargs):
        interval = int(self.context.get('interval'))        
        candlesticks = obj.get_candlestick_data(interval=interval)
        return candlesticks