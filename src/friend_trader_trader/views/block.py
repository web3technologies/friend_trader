from rest_framework.viewsets import ReadOnlyModelViewSet

from friend_trader_core.mixins import ThrottleMixin
from friend_trader_trader.models import Block
from friend_trader_trader.serializers.block_detail import BlockDetailSerializer


class BlockViewset(ReadOnlyModelViewSet, ThrottleMixin):
    queryset = Block.objects.all().prefetch_related("trade_set__prices")
    serializer_class = BlockDetailSerializer
    lookup_field = "block_number"
    