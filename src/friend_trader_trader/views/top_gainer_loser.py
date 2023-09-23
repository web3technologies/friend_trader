import datetime
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView
from django.db.models import Case, When, F, Sum
from friend_trader_trader.models import Trade, Price
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.db.models import DecimalField, F, FloatField, Max, Min, OuterRef, Subquery, Value


class TopGainerLoserView(APIView):
    
    # @method_decorator(cache_page(60*15), name="dispatch")
    def get(self, request, *args, **kwargs):
        
        def date_to_unix_timestamp(d):
            return int(d.timestamp())
        
        today = datetime.date.today()

        start_of_day = datetime.datetime(today.year, today.month, 5) - datetime.timedelta(days=1)
        end_of_day = start_of_day + datetime.timedelta(days=1)

        start_unix = date_to_unix_timestamp(start_of_day)
        end_unix = date_to_unix_timestamp(end_of_day)
        
        first_prices = Price.objects.filter(
            trade__block__block_timestamp__gte=start_unix, 
            trade__block__block_timestamp__lt=end_unix
        ).order_by('trade__subject', 'trade__block__block_timestamp', 'id').distinct('trade__subject').values('trade__subject', 'price')

        last_prices = Price.objects.filter(
            trade__block__block_timestamp__gte=start_unix, 
            trade__block__block_timestamp__lt=end_unix
        ).order_by('trade__subject', 'trade__block__block_timestamp', '-id').distinct('trade__subject').values('trade__subject', 'price')

        subjects_with_changes = Trade.objects.filter(
            block__block_timestamp__gte=start_unix, 
            block__block_timestamp__lt=end_unix
        ).annotate(
            first_price_of_day=Subquery(
                first_prices.filter(trade__subject=OuterRef('subject')).values('price')[:1],
                output_field=DecimalField(max_digits=45, decimal_places=20)
            ),
            last_price_of_day=Subquery(
                last_prices.filter(trade__subject=OuterRef('subject')).values('price')[:1],
                output_field=DecimalField(max_digits=45, decimal_places=20)
            )
        ).annotate(
            total_price_change=F('last_price_of_day') - F('first_price_of_day'),
            percent_change=Case(
                When(first_price_of_day=0, then=Value(None)),
                default=(F("total_price_change") / F("first_price_of_day")) * 100,
                output_field=FloatField()
            )
        ).values('subject', 'total_price_change', 'percent_change').distinct('subject')


        
        # today_trades = Trade.objects.filter(block__block__block_timestamp__gte=start_unix, block__block__block_timestamp__lt=end_unix)


        # subjects_gain_or_loss = today_trades.annotate(
        #     net_amount=Case(
        #         When(is_buy=True, then=F('price')),
        #         When(is_buy=False, then=-F('price')),
        #         default=0,
        #         output_field=DecimalField(max_digits=45, decimal_places=20)
        #     )
        # ).values('subject').annotate(total_net=Sum('net_amount')).order_by('-total_net')
        # top_5_gainers = subjects_gain_or_loss[:5]
        # top_5_losers = subjects_gain_or_loss.reverse()[:5]
            
        return Response(data={"top_5_gainers": subjects_with_changes, "top_5_losers": subjects_with_changes}, status=HTTP_200_OK)