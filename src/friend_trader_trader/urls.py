from django.urls import path
from rest_framework import routers

from friend_trader_trader.views import BlockViewset, FriendTechUserViewSet, FriendTechUserListView, ProtocolMetrics, TradeListView, TradeViewSet, TradeVolumeView, TopGainerLoserView, FriendTechUserWatchListViewset

# Routers provide a way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'friend-tech-user', FriendTechUserViewSet)
router.register(r"block", BlockViewset)
router.register(r"trade", TradeViewSet)
router.register(r"watchlist", FriendTechUserWatchListViewset)


urlpatterns = [
    path("friend-tech-user-list/", FriendTechUserListView.as_view()),
    path("trades/<str:address>/", TradeListView.as_view()),
    # path("protocol-metrics/", ProtocolMetrics.as_view()),
    path("volume/", TradeVolumeView.as_view()),
    # path("top-gainer-loser/", TopGainerLoserView.as_view())
]

urlpatterns += router.urls