import datetime
import pytz
import time as Time
from rest_framework import serializers

from friend_trader_trader.models import FriendTechUser


class FriendTechUserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = FriendTechUser
        fields = "__all__"
        
        

class FriendTechUserCandleStickSerializer(FriendTechUserSerializer):
    
    candle_stick_data = serializers.SerializerMethodField("generate_candlestick")
    first_trade = serializers.SerializerMethodField("get_first_trade")
    last_trade = serializers.SerializerMethodField("get_last_trade")
    
    def __convert_to_central_time(self, eth_timestamp):
        utc_time = datetime.datetime.utcfromtimestamp(eth_timestamp)
        utc_time = pytz.utc.localize(utc_time)
        central_time = utc_time.astimezone(pytz.timezone('US/Central'))
        formatted_time = central_time.strftime('%Y-%m-%d %I:%M:%S %p')
        return formatted_time
    
    def get_first_trade(self, obj):
        return self.__convert_to_central_time(obj.share_prices.order_by("block__block_timestamp").first().block.block_timestamp)
    
    def get_last_trade(self, obj):
        return self.__convert_to_central_time(obj.share_prices.order_by("block__block_timestamp").last().block.block_timestamp)
    
    def generate_candlestick(self, obj, *args, **kwargs):
        interval = int(self.context.get('interval'))
        data = obj.share_prices.select_related("block").all().order_by("block__block_timestamp").values("price", "block__block_timestamp")
        
        if not data:
            return []

        start_time = data[0]['block__block_timestamp']
        end_time = start_time + interval

        candlesticks = []
        last_known_price = data[0]['price']
        current_candle = {
            'Open': last_known_price,
            'Close': last_known_price,
            'High': last_known_price,
            'Low': last_known_price,
            'Start_Time': self.__convert_to_central_time(start_time),
            'End_Time': self.__convert_to_central_time(end_time)
        }

        for entry in data:
            time_stamp, price = entry['block__block_timestamp'], entry['price']

            while time_stamp >= end_time:
                candlesticks.append(current_candle)

                start_time = end_time
                end_time = start_time + interval
                current_candle = {
                    'Open': last_known_price,
                    'Close': last_known_price,
                    'High': last_known_price,
                    'Low': last_known_price,
                    'Start_Time': self.__convert_to_central_time(start_time),
                    'End_Time': self.__convert_to_central_time(end_time)
                }

            current_candle['Close'] = price
            current_candle['High'] = max(current_candle['High'], price)
            current_candle['Low'] = min(current_candle['Low'], price)
            last_known_price = price

        candlesticks.append(current_candle)

        current_unix_time = int(Time.time())
        while end_time <= current_unix_time:
            start_time = end_time
            end_time = start_time + interval
            current_candle = {
                'Open': last_known_price,
                'Close': last_known_price,
                'High': last_known_price,
                'Low': last_known_price,
                'Start_Time': self.__convert_to_central_time(start_time),
                'End_Time': self.__convert_to_central_time(end_time)
            }
            candlesticks.append(current_candle)

        return candlesticks