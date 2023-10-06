from django.utils import timezone

from rest_framework import serializers

from friend_trader_core.utils import convert_to_central_time
from friend_trader_trader.models import FriendTechUser, Price
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
    twenty_four_hour_percent_change = serializers.SerializerMethodField("get_twenty_four_hour_percent_change")
    seven_day_percent_change = serializers.SerializerMethodField("get_seven_day_percent_change")
    
    class Meta:
        model = FriendTechUser
        fields = ("id", "twitter_username", "twitter_profile_pic", "twitter_followers", "latest_price", "shares_supply", "last_trade_time", "twenty_four_hour_percent_change", "seven_day_percent_change")
    
    def get_last_trade_time(self, obj, *args, **kwargs):
        if last_trade := obj.share_prices.select_related("block").order_by("block__block_timestamp").last():
            return last_trade.block.block_timestamp
        else:
            return None
        
    def get_twenty_four_hour_percent_change(self, obj, *args, **kwargs):
        twenty_four_hours_ago = timezone.now() - timezone.timedelta(days=1)
        twenty_four_hours_ago_unix = int(twenty_four_hours_ago.timestamp())

        first_price_since_24_hours_ago = Price.objects.filter(
            trade__subject=obj, 
            trade__block__block_timestamp__gte=twenty_four_hours_ago_unix
        ).order_by("trade__block__block_timestamp").first()

        if not first_price_since_24_hours_ago:
            return 0
         
        if obj.latest_price.price == 0:
            return 0
        percent_change = (1 - (first_price_since_24_hours_ago.price / obj.latest_price.price)) * 100
        return percent_change
        
    def get_seven_day_percent_change(self, obj, *args, **kwargs):
        seven_days_ago = timezone.now() - timezone.timedelta(days=7)
        seven_days_ago_unix = int(seven_days_ago.timestamp())
        first_price_since_seven_days_ago = Price.objects.filter(
            trade__subject=obj, 
            trade__block__block_timestamp__gte=seven_days_ago_unix
        ).order_by("trade__block__block_timestamp").first()
        
        if not first_price_since_seven_days_ago:
            return 0 

        if not obj.latest_price or obj.latest_price.price == 0:
            return 0

        percent_change = (1 - (first_price_since_seven_days_ago.price / obj.latest_price.price)) * 100

        return percent_change
    

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