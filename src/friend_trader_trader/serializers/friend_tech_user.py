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
        central_time = central_time.strftime('%Y-%m-%dT%H:%M:%S')
        return eth_timestamp
    
    def get_first_trade(self, obj):
        return self.__convert_to_central_time(obj.share_prices.order_by("block__block_timestamp").first().block.block_timestamp)
    
    def get_last_trade(self, obj):
        return self.__convert_to_central_time(obj.share_prices.order_by("block__block_timestamp").last().block.block_timestamp)
    
    def generate_candlestick(self, obj, *args, **kwargs):
        interval = int(self.context.get('interval'))
        data = obj.share_prices.select_related("block").all().order_by("block__block_timestamp").values("price", "block__block_timestamp")
        
        if not data:
            return []

        time = (data[0]['block__block_timestamp'] // interval) * interval
        end_time = time + interval

        candlesticks = []
        last_known_price = data[0]['price']
        current_candle = {
            'open': last_known_price,
            'close': last_known_price,
            'high': last_known_price,
            'low': last_known_price,
            'time': self.__convert_to_central_time(time),
            # 'End_Time': self.__convert_to_central_time(end_time)
        }

        for entry in data:
            time_stamp, price = entry['block__block_timestamp'], entry['price']

            # check if current time is within the current candle stick defined by end_time
            while time_stamp >= end_time:
                candlesticks.append(current_candle)

                # essentially produce another candle and extend the time to the next candle
                # eventually the timestamp will be less than the end time
                time = end_time
                end_time = time + interval
                current_candle = {
                    'open': last_known_price,
                    'close': last_known_price,
                    'high': last_known_price,
                    'low': last_known_price,
                    'time': self.__convert_to_central_time(time),
                    # 'End_Time': self.__convert_to_central_time(end_time)
                }

            current_candle['close'] = price
            current_candle['high'] = max(current_candle['high'], price)
            current_candle['low'] = min(current_candle['low'], price)
            last_known_price = price

        candlesticks.append(current_candle)

        current_unix_time = int(Time.time())
        while end_time <= current_unix_time:
            time = end_time
            end_time = time + interval
            current_candle = {
                'open': last_known_price,
                'close': last_known_price,
                'high': last_known_price,
                'low': last_known_price,
                'time': self.__convert_to_central_time(time),
                # 'End_Time': self.__convert_to_central_time(end_time)
            }
            candlesticks.append(current_candle)

        return candlesticks