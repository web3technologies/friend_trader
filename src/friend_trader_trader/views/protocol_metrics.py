import time
from datetime import timedelta
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from friend_trader_core.mixins import ThrottleMixin
from friend_trader_trader.models import Price


class ProtocolMetrics(APIView, ThrottleMixin):
    
    model = Price
    
    @method_decorator(cache_page(60*15), name="dispatch")
    def get(self, request, *args, **kwargs):

        now_unix = int(time.time())
        one_day_ago_unix = now_unix - int(timedelta(days=1).total_seconds())

        prices = self.model.objects.select_related("trade__block").filter(trade__block__block_timestamp__gte=one_day_ago_unix)
        total_volume = 0
        for price in prices:
            total_volume += price.price
            
        return Response(data={"total_volume": total_volume}, status=HTTP_200_OK)