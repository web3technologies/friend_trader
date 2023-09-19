
from datetime import timedelta
from django.db.models import Sum
from django.db.models.functions import TruncMonth, TruncDay, TruncWeek
from django.db.models import DateField, ExpressionWrapper, F
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response

from friend_trader_trader.models import Trade
from friend_trader_trader.serializers.volume_serializer import VolumeSerializer



class TradeVolumeView(APIView):
    
    def get(self, request, *args, **kwargs):
        
        period = self.request.query_params.get("period")
        if period not in ("day", "week", "month"):
            return Response(data={"period must either be: day, week, month"})
        if period == "day":
            trunc_class = TruncDay
        elif period == "week":
            trunc_class = TruncWeek
        else:
            trunc_class = TruncMonth
        
        end_date = timezone.now()
        start_date = end_date - timedelta(days=365)
        start_timestamp = int(start_date.timestamp())
        end_timestamp = int(end_date.timestamp())
        
        timestamp_to_date = ExpressionWrapper(
            timezone.datetime(1970, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=1) * F('block__block_timestamp'),
            output_field=DateField()
        )

        volumes = (
            Trade.objects.filter(block__block_timestamp__gte=start_timestamp, block__block_timestamp__lte=end_timestamp)
            .annotate(date=timestamp_to_date)
            .annotate(**{period: trunc_class('date')})
            .values(period)
            .annotate(value=Sum('price'))
            .order_by(period)
        )

        serialized_data = VolumeSerializer(volumes, many=True).data

        return Response(serialized_data)