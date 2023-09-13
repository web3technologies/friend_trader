from django.urls import path
from rest_framework import routers

from friend_trader_trader.views import BlockViewset, FriendTechUserViewSet, FriendTechUserListView, ProtocolMetrics, TradeListView, TradeViewSet 

# Routers provide a way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'friend-tech-user', FriendTechUserViewSet)
router.register(r"block", BlockViewset)
router.register(r"trade", TradeViewSet)


urlpatterns = [
    path("friend-tech-user-list/", FriendTechUserListView.as_view()),
    path("trades/<str:address>/", TradeListView.as_view()),
    path("protocol-metrics/", ProtocolMetrics.as_view())
]

urlpatterns += router.urls