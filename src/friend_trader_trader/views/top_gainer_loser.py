import datetime
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.db.models import DecimalField, F, FloatField, Max, Min, OuterRef, Subquery, Value,  Case, When, F, Window, Q
from django.db.models.functions import RowNumber

from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView

from friend_trader_core.mixins import ThrottleMixin
from friend_trader_trader.models import Trade, Price


class TopGainerLoserView(APIView, ThrottleMixin):

    def date_to_unix_timestamp(self, d):
        return int(d.timestamp())
    
    # @method_decorator(cache_page(60*15), name="dispatch")
    def get(self, request, *args, **kwargs):
        today = datetime.date.today()

        start_of_day = datetime.datetime(today.year, today.month, 20) - datetime.timedelta(days=1)
        end_of_day = start_of_day + datetime.timedelta(days=1)

        start_unix = self.date_to_unix_timestamp(start_of_day)
        end_unix = self.date_to_unix_timestamp(end_of_day)
        
        prices_at_time = Price.objects.filter(
            trade__block__block_timestamp__gte=start_unix, 
            trade__block__block_timestamp__lt=end_unix
        ).annotate(
            rank=Window(expression=RowNumber(),
                        order_by=F('trade__block__block_timestamp').asc()),
            rank_desc=Window(expression=RowNumber(),
                            order_by=F('trade__block__block_timestamp').desc())
        ).filter(Q(rank=1) | Q(rank_desc=1))

        subjects_with_changes = Trade.objects.filter(
            block__block_timestamp__gte=start_unix, 
            block__block_timestamp__lt=end_unix
        ).annotate(
            first_price_of_day=Subquery(
                prices_at_time.filter(trade__subject=OuterRef('subject'), rank=1).values('price')[:1],
                output_field=DecimalField(max_digits=45, decimal_places=20)
            ),
            last_price_of_day=Subquery(
                prices_at_time.filter(trade__subject=OuterRef('subject'), rank_desc=1).values('price')[:1],
                output_field=DecimalField(max_digits=45, decimal_places=20)
            )
        ).annotate(
            total_price_change=F('last_price_of_day') - F('first_price_of_day'),
            percent_change=Case(
                When(first_price_of_day=0, then=Value(None)),
                default=(F("total_price_change") / F("first_price_of_day")) * 100,
                output_field=FloatField()
            )
        ).distinct('subject', "total_price_change").order_by("subject", "total_price_change").values('subject__twitter_username', 'total_price_change', 'percent_change')

        return Response(data={
            "top_5_gainers": list(subjects_with_changes[:5]),
            "top_5_losers": list(subjects_with_changes.reverse()[:5])
        }, status=HTTP_200_OK)
    



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