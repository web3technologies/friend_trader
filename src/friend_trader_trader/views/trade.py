from django.db.models import F, Count

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from friend_trader_trader.models import Trade
from friend_trader_trader.serializers import TradeListSerializer


class TradeListView(APIView):
    
    serializer_class = TradeListSerializer
    queryset = Trade.objects.all()
    
    def get(self, request, address, *args, **kwargs):
        users = self.queryset.filter(subject__address=address).order_by("-block__block_number")
        user_data = self.serializer_class(users, many=True)
        return Response(data=user_data.data[0:10], status=HTTP_200_OK)
