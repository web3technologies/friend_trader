from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.exceptions import NotFound

from friend_trader_trader.models import Block
from friend_trader_trader.serializers.block_detail import BlockDetailSerializer


class BlockViewset(ReadOnlyModelViewSet):
    queryset = Block.objects.all().prefetch_related("trade_set__prices")
    serializer_class = BlockDetailSerializer
    lookup_field = "block_number"
    