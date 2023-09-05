import datetime
import pytz

from rest_framework import serializers

from friend_trader_trader.models import FriendTechUser


class FriendTechUserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = FriendTechUser
        fields = "__all__"
        
        

class FriendTechUserCandleStickSerializer(FriendTechUserSerializer):
    
    candle_stick_data = serializers.SerializerMethodField("generate_candlestick")
    
    def __convert_to_central_time(self, eth_timestamp):
        utc_time = datetime.datetime.utcfromtimestamp(eth_timestamp)
        utc_time = pytz.utc.localize(utc_time)
        central_time = utc_time.astimezone(pytz.timezone('US/Central'))
        formatted_time = central_time.strftime('%Y-%m-%d %I:%M:%S %p')
        return formatted_time
    
    def generate_candlestick(self, obj, *args, **kwargs):
        interval = int(self.context.get('interval'))
        data = obj.share_prices.all().order_by("block__block_timestamp").values("price", "block__block_timestamp")
        
        if not data:
            return []

        # Initialize the first bucket
        start_time = data[0]['block__block_timestamp']
        end_time = start_time + interval

        candlesticks = []
        current_candle = {
            'Open': data[0]['price'],
            'Close': data[0]['price'],
            'High': data[0]['price'],
            'Low': data[0]['price'],
            'Start_Time': self.__convert_to_central_time(start_time),
            'End_Time': self.__convert_to_central_time(end_time)
        }

        for entry in data:
            time, price = entry['block__block_timestamp'], entry['price']

            # Check if the time is within the current interval
            if start_time <= time < end_time:
                current_candle['Close'] = price
                current_candle['High'] = max(current_candle['High'], price)
                current_candle['Low'] = min(current_candle['Low'], price)
            else:
                # Append the completed candlestick to the results
                candlesticks.append(current_candle)

                # Start a new candlestick interval
                start_time = time
                end_time = start_time + interval
                current_candle = {
                    'Open': price,
                    'Close': price,
                    'High': price,
                    'Low': price,
                    'Start_Time': self.__convert_to_central_time(start_time),
                    'End_Time': self.__convert_to_central_time(end_time)
                }

        # Add the last interval if it hasn't been added
        if current_candle not in candlesticks:
            candlesticks.append(current_candle)

        return candlesticks
